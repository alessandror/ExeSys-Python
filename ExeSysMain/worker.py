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
import redis

import redis_scripts as rs
import environment as env

module = __import__(env.FUNCT_MODULE, globals(), locals(), [env.FUNCT], -1)
exef = getattr(module, env.FUNCT)
print ">>> current module, function_script: " ,module,exef
import cPickle 
import time
import json
import sys

def worker(worker_num, redis_addr, redis_port, redis_db):
    worker_num = worker_num
    pool = redis.ConnectionPool(host=redis_addr, port=redis_port, db=redis_db)
    redisconn = redis.Redis(connection_pool=pool)
    worker_exe_logic_new(redisconn,worker_num)

def worker_exe_logic_new(redisconn, worker_num):
    startjob_script = redisconn.register_script(rs.worker_start_job())
    endjob_script = redisconn.register_script(rs.worker_end_job())
    process_chain_job_script = redisconn.register_script(rs.worker_process_chain_job())
    job_reply = {}
    while True:
        module_function_and_data = None

        while module_function_and_data == None:
            module_function_and_data = startjob_script(keys=['*:*:start'], args=[])
            time.sleep(0.1)
        
        if module_function_and_data != None:
            print "\n--------------------------- worker #%s new job with command %s" % (str(worker_num), module_function_and_data)
            data = json.loads(module_function_and_data)
            
            #tricky check if data is pickled
            try:
                module_data = cPickle.loads(data['data'])
            except:
                module_data =  data['data']

            module_function =  data['cmd']
            module_jobid    =  data['job_id']
            module_jobfrom  =  data['job_from']
            
            #functions may not exist or failure logging and go on
            try:
                f = getattr(exef, module_function)
                job_reply = f(module_data)
            except Exception,error:
                print ">>> Worker unexpected error:", sys.exc_info()[0]
                err = "worker exception error:" + str(error)
                if env.LOGGING == 1:
                    redisconn.set('worker_ex:' + module_jobid + ':' + str(worker_num), err)

                job_reply['EOJ'] = err
                job_reply['type'] = 'exception'


            if "EOJ" in job_reply.keys():
                datap = ""
                if env.LOGGING == 1:
                    redisconn.set('EOJ:' + str(worker_num) + ':' + module_jobid, 'ok')
                
                #print "--- worker job_from %s" % data['to']  
                if "end_job" in data['to']:
                    datap = cPickle.dumps(job_reply['EOJ'])
                    #print "--> worker end job send pickled result: %s" % (datap)

                endjob_script(keys=['*:' + module_jobid + ':processing'], args = [module_jobfrom,
                                                                                  module_jobid,
                                                                                  datap])
                
        #process workflow jobs if there are keys with data_available status and not to:end_job 
        status = process_chain_job_script(keys=['*:*:data_available'], args=[])
        #print "status : %s" % (str(status))

    time.sleep(0.5)
     
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', type=int)
    args = parser.parse_args()
    worker(args.w, env.REDISIP, env.REDISPORT, env.REDISSYSDB)
    
    
    
    
    