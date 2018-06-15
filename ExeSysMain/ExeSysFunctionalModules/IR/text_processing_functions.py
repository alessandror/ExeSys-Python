"""
Copyright 2018 Alex Redaelli <a.redaelli at gmail dot com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, 
modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the 
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR 
THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

#-*- coding: utf-8 -*-
import json
import collections
import uuid
import datetime
import time
import subprocess
import sys
import os
import glob
from jnius import autoclass

import redis

import tokenizer

# -- functional imports
base_dir = os.path.dirname(__file__) or '.'
sys.path.insert(0, base_dir + '/../../')

sys.path.insert(0, base_dir + '/../ExeSysFunc/') 

import environment as env

pool = redis.ConnectionPool(host=env.REDISIP, port=env.REDISPORT, db=env.REDISDATADB)
redisconn = redis.Redis(connection_pool=pool)

pool1 = redis.ConnectionPool(host=env.REDISIP, port=env.REDISPORT, db=env.REDISSYSDB)
redisconn1 = redis.Redis(connection_pool=pool1)

jars_directory = os.path.join(os.path.dirname(__file__), 'tika')
CLASSPATH = []
for jar_path in glob.iglob(os.path.join(jars_directory, "*.jar")):
    CLASSPATH.append(jar_path)

os.environ["CLASSPATH"] = os.path.pathsep.join(CLASSPATH)

System = autoclass('java.lang.System')
System.setProperty("java.awt.headless", "true")
print "\n\nClass Path:", System.getProperty('java.class.path')
print ">>>>> tika jar dir: %s" %  os.getcwd() + "/tika/tika-app-1.4.jar"


def tika_processing(filename):
    try:
        Tika = autoclass('org.apache.tika.Tika')
        Metadata = autoclass('org.apache.tika.metadata.Metadata')
        Lang = autoclass('org.apache.tika.language.LanguageIdentifier')
        FileInputStream = autoclass('java.io.FileInputStream')

        cur_tika = Tika()
        cur_meta = Metadata()
        cur_tika.setMaxStringLength(-1)

        print "\n>>>>>>>> in tika_processing filename: %s" % filename
        text = cur_tika.parseToString(FileInputStream(filename),cur_meta)

        #print text
        lang = Lang(text.decode("utf-8"))
        langid = lang.getLanguage()
        #doc_hash= hashlib.sha1(text).hexdigest()
        doc_hash= str(uuid.uuid4())
        redisconn.sadd('doc_to_tokenize_set',doc_hash)
        redis_key = "docdata:" + doc_hash + ":0" # -- default no tokenized
        redisconn.hset(redis_key,'text_data', text)
        redisconn.hset(redis_key,'filename', filename)
        redisconn.hset(redis_key,'lang',langid) 
        redisconn.hset(redis_key,'import_date', str(datetime.datetime.now()))
    except Exception :
        redisconn.set('ir_ex:' + filename + ':' + str(sys.exc_info()[0]),'ouch')

def create_tika_import_job(filename):
    jid = str(uuid.uuid4())
    redis_exe_key="txt_proc_funct:" + jid + ":start"
    redisconn1.hset(redis_exe_key,"to","end_job")
    redisconn1.hset(redis_exe_key,"cmd","tika_read_document") 
    redisconn1.hset(redis_exe_key,"data",'[\"filesys-folder-single\",' + \
                                          '\"' + filename + '\"]')
    return jid

def tika_read_document(data_to_process):
    ''' read document and save text data
        data_to_process[0] subcommand filesys-single / filesys-folder
                       [1] data_source_param (filename)
                       [2] data_sink'''
                     
    print "\n>>>>>>>> in tika_read_document with data to process %s" % data_to_process
    resp = {}
    if "filesys-single" in data_to_process[0]:
        tika_processing(data_to_process[1])
        resp_text = '[\"filesys-single\",' + '\"imported' + '\"]'
        resp['EOJ'] = resp_text
        resp['type'] = 'redis'
        return resp
    elif "filesys-folder-single" in data_to_process[0]:
        print "\n--- processing file single"
        tika_processing(data_to_process[1])
        resp_text = '[\"filesys-single\",' + '\"imported' + '\"]'
        resp['EOJ'] = resp_text
        resp['type'] = 'redis'
        return resp
    elif "filesys-folder" in data_to_process[0]:
        filelist = os.listdir(data_to_process[1])
        import_doc_job_list=[]
        poll_jobs_status = True
        start_time = datetime.datetime.now()
        num_files_to_import = len(filelist)
        tot_size = 0
        #create import job list
        for infile in filelist:
            path = data_to_process[1] + infile
            jid = create_tika_import_job(path)
            import_doc_job_list.append(jid)
            tot_size = tot_size + os.path.getsize(path)
            
        #wait until all jobs are done
        while poll_jobs_status:
            for jid in import_doc_job_list:
                redis_key= redisconn1.keys('txt_proc_funct:' + jid + ':*') #TODO: da cambiare 
                if len(redis_key) >0:
                    if 'data_available' in redis_key[0]:                    
                        redisconn1.delete(redis_key[0])
                        print "\n>>>>> deleted key %s" % redis_key
                        import_doc_job_list.remove(jid)
            if len(import_doc_job_list)==0:
                poll_jobs_status=False
                break
            time.sleep(1)
        elapsedTime = datetime.datetime.now() - start_time
        resp_text = '[\"filesys-folder\",' + '\"imported ' + str(tot_size) + \
                     ' bytes ' + str(num_files_to_import) + \
                     ' files in[s]:'+ str(elapsedTime.total_seconds()) + '\"]'
        resp['EOJ'] = json.loads(resp_text)
        resp['type'] = 'redis'
        return resp
    else:
        resp['EOJ'] = "not supported"
        resp['type'] = 'n/a'
        return resp

def regex_tokenizer(data_to_process):
    ''' nltk regex tokenizer
        data_to_process[0] data_source
        data_to_process[1] doc_to_tokenize_set

        data must be in format docdata:doc_hash:tokenize_status  = { filename: xxx,
                                                                     import_date: xxx,
                                                                     lang: xxx,
                                                                     text_data : xxx,
                                                                     num_doc_tokens : xxx }'''
    
    print "\n------------------------------------------- in regex_tokenzer with data to process %s" % data_to_process
    
    resp = {}
    if  "redis" in data_to_process[0]:
        start = time.time()
        doc_to_tokenize_set = data_to_process[1]
        while True:
            # -- get redis key docdata:doc_hash:tokenize_status 
            doc_hash_to_tokenize = redis.pop(doc_to_tokenize_set)
            if doc_hash_to_tokenize != None:
                # -- replace key tokenize flag with 1
                doc_key = "docdata:"+ doc_hash_to_tokenize + ":0" 
                new_key = "docdata:"+ doc_hash_to_tokenize + ":1" 
                redisconn.rename(doc_key, new_key)
                # -- get doc language
                doc_lang = redisconn.hget(new_key,"lang")
                # -- get doc text
                doc_text = redisconn.hget(new_key,"text_data")
                # -- process one key at a time leave other key to other processes #TODO: bulk 
                extracted_tokens = tokenizer.Tokenizer(os.getcwd() +'/ExeSysFunctionalModules/IR/stopwords.txt').tokenize_file( doc_text )
                num_token_in_extracted_tokens = extracted_tokens['number_token_list']
                # -- save number of document's tokens
                redisconn.hset(new_key,"num_doc_tokens", num_token_in_extracted_tokens)
                # -- token counter
                token_counter = collections.Counter(extracted_tokens['word_token_list'])
                # -- building dictionaries
                for token in extracted_tokens['word_token_list']:
                    # -- refine: remove punctuation 
                    #exclude = set(string.punctuation)
                    #token_refined = ''.join(ch for ch in token if ch not in exclude)
                    # -- refine: remove punctuation and articles 
                    if 'it' in doc_lang:
                        for punctuation, tag in (
                          (u".", ""), (u"-",""),
                          (u"d'",""), (u"nell'",""),
                          (u"all'",""), (u"niun'",""),
                          (u"s'",""),("agl'","")  ):
                            if punctuation in token:
                                token = token.replace(punctuation,tag)
  
                    # -- refine: normalize words
                        # -- check with main dictionary
#                     if  redisconn1.exists("wdmain::"+ token + ":*:*:*")=="1":
#                         pass
                        # -- tagging
                        
                    # -- feature extraction 
                        # -- gazetteer
                        
                    # -- calc token frequency in document
                    token_freq = (float(token_counter[token]) / float(num_token_in_extracted_tokens))
                    # -- save corpus token data 
                    redis_key = "wd:" + token + ":" + doc_lang 
                    redisconn.rpush(redis_key, str(doc_hash_to_tokenize) + "|" + str( token_freq ))
            else:
                break
            stop = time.time()
        resp_text = '[\"regex-tokenizer\",' + '\"processed_files in[ms]:' + str((stop-start)*1000) + '\"]'
        resp['EOJ'] = json.loads(resp_text)
        return resp
        
    resp['EOJ'] = "not supported"
    return resp
  
def opennlp_tokenizer(data_to_process):
    resp = {}
    model = data_to_process[0]
    data = data_to_process[1]
    funct =  data_to_process[1]
    result = subprocess.Popen(['/Users/alexr/Downloads/apache-opennlp-1.5.3/bin/opennlp',funct,model,data], shell=False)
    resp['EOJ'] = result
    return resp

if __name__ == '__main__':
    tika_processing("/Users/alessandror/test_docs/pdf_aifa/10.rtprogramming-handout.pdf")

