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

import pprint
import math
import operator

import redis

from ExeSysMain import environment as env


class Searcher():
    
    def __init__( self ):
        self.corpus_doc_average_len = 0
        self.cur_search = {}
        
        self.pool = redis.ConnectionPool(host=env.REDISIP, port=env.REDISPORT, db=env.REDISDATADB)
        self.redisconn = redis.Redis(connection_pool=self.pool) 

# -- total docs in corpus
        redis_key = "docdata:*:1"
        self.documents_in_corpus = self.redisconn.keys(redis_key)
        self.tot_doc_in_corpus = len(self.documents_in_corpus)
        
# -- average doc len in corpus
        self.corpus_doc_avg_len = 0.0
        self.corpus_doc_len_tot = 0.0
        for cur_doc_key in self.documents_in_corpus:
            cur_doc_len = self.redisconn.hget(cur_doc_key,"num_doc_tokens")
            self.corpus_doc_len_tot = self.corpus_doc_len_tot + float(cur_doc_len)
        self.corpus_doc_avg_len = self.corpus_doc_len_tot / float(self.tot_doc_in_corpus )
        
    def init_query(self, query_word_list):
        self.doc_set_hash = []
        self.query_word_list = query_word_list

# -- get all docs id with query words
        for word in query_word_list:
            redis_key = "worddict:" + word + ":*:*:*"
            doc_list = self.redisconn.get(redis_key)
            for doc in doc_list:
                self.doc_set_hash.append(doc)
                
# -- ranking with bm25f       
    def bm25f(self, k1=2.0, b=0.75):
        doc_score = {}
        kvalue0 = k1+1
        kvalue1 = k1*(1-b+b*(self.tot_doc_in_corpus / self.corpus_doc_avg_len ) )
        for doc_hash in self.doc_set_hash:

            redis_key = "docdata:" + doc_hash + ":1"
            filename = self.redisconn.hget(redis_key,"filename")
            score = 0.0
            for query_word in self.query_word_list:
                            
                redis_key = "worddict:" + query_word + ":*:*:*"
                query_word_doc_list  =  self.redisconn.lrange(redis_key, 0, -1)
                query_word_doc_list_len = len( query_word_doc_list )
                
                word_idf = self.calc_idf( query_word_doc_list_len )
                
                for doc in query_word_doc_list:
                    cur_doc_data = doc.split("|") ## -- [..., dochash!freq, ...]
                    if  cur_doc_data[0] == doc_hash:
                        word_freq_in_doc_D = float( cur_doc_data[1] )
                
                if word_freq_in_doc_D != None:
                    num = ( float( word_freq_in_doc_D ) * kvalue0)
                    den = ( float( word_freq_in_doc_D ) + kvalue1) 
                    score = score + word_idf * ( num / den )
                    
            doc_score[filename] = score
            sorted_doc_score = sorted(doc_score.iteritems(), key=operator.itemgetter(1), reverse = True) 
            self.cur_search["query_results"] = sorted_doc_score
                  
    def calc_idf(self,num_of_doc_with_query_word):
        num = ( float(self.tot_doc_in_corpus) - float(num_of_doc_with_query_word) + 0.5 )
        den = ( float(float(num_of_doc_with_query_word) + 0.5 ))
        idf = math.log( (num/den) )
        if idf <= 0: 
            return 0
        else:
            return idf    

    def get_sorted_results(self):
        return  self.cur_search
    
if __name__ == '__main__':
    print "-> start search test"
    cur_searcher = Searcher(  ) 
    cur_searcher.init_query( ["testword0","testword1"] ) 
    print "--> searching..."
    cur_searcher.bm25f()
    print "--> print results"
    results = cur_searcher.get_sorted_results()
    pprint.pprint(results)

    
    