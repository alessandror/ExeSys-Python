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

import threading
import requests
import json
import uuid
import time
import redis

class ExeSysTest(threading.Thread):
    
    def __init__(self):
        self.RUNSINGLE = 0
        self.RUNWORKFLOW= 1
        self.RUNTYPE = None
        self.redis_addr = '127.0.0.1'
        self.redis_port = 6380 
        self.redis_db = 0
        self.test_url= ""
        self.end_job='end-job'
        self.jobs_list= []
        self.end_job_list= []
        self.running = False
        self.pool = redis.ConnectionPool( host=self.redis_addr, 
                                          port=self.redis_port, 
                                          db=self.redis_db)
        self.redisconn = redis.Redis(connection_pool=self.pool)
        self.timeout_get_resp = 0.1
        threading.Thread.__init__(self)
        
    def set_payload(self, cfrom='', to='', cmd='', data=[], job_id='' ):
        payload= {'from': cfrom, 
                  'to': to, 
                  'cmd': cmd, 
                  'data': data, 
                  'job_id': job_id }
        return payload
    
    def set_headers(self,operation_type):
        if 'single' in operation_type:
            headers_single_operation = {'content-type': 'application/json'}
            return headers_single_operation
        if 'workflow' in operation_type:
            headers_workflow = {'content-type' : 'application/json', 
                                'Operation'    : 'workflow'}
            return headers_workflow
        return 'fail'
    
    def set_job_uuid(self):
        return uuid.uuid4()
    
    def set_job(self,url, payload, headers):
        job= {'url': url, 
              'payload': payload, 
              'headers': headers}
        self.jobs_list.append(job)
        if payload['to'] == 'end_job':
            self.end_job_list.append(job)
    
    def send_post(self,url,payload,headers):
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        return r.text
    
    def set_timeout_get_resp(self,timeout_time):
        self.timeout_get_resp = timeout_time
        
    def run(self):
        # -- start jobs
        for job in self.jobs_list:
            if len(job) > 0:
                resp = self.send_post(job['url'], 
                                      job['payload'], 
                                      job['headers'])
    
        while(self.running):
             
            if (self.RUNTYPE == self.RUNSINGLE):
                # -- poll for response single or more jobs
                for job in self.jobs_list:
                    if len(job) > 0:
                        # -- send command
                        resp = self.send_post(job['url'], 
                                              job['payload'], 
                                              job['headers'])

                        # -- check resp
                        #print "\n>>>>>>>> resp %s" % resp
                        if 'data_available' in resp:
                            job_id = job['payload']['job_id']
                            resp_json = json.loads(resp)
                            if type(resp_json) == list:
                                print "-->job_id: %s resp: [%s]" % (job_id, ', '.join(map(str, resp_json['data'])))
                            print "-->job_id: %s resp: [%s]" % (job_id, str(resp_json['data']))
                            self.redisconn.delete("*:" + job_id + ":*")
                            self.jobs_list.remove(job)
                                
                        time.sleep(self.timeout_get_resp)
                       
                if len(self.jobs_list)==0:
                    break
                 
            if (self.RUNTYPE == self.RUNWORKFLOW):
                for end_job in self.end_job_list:
                    req_header = {'content-type': 'application/json'}
                    end_job['headers'] = req_header # -- the result request not need workflow xheader and must be last commond in chain
                    resp = self.send_post(end_job['url'], 
                                          end_job['payload'], 
                                          end_job['headers'])
                    # -- check resp
                    #print "--> resp %s" % resp
                    if 'data_available' in resp:
                        job_id = end_job['payload']['job_id']
                        resp_json = json.loads(resp)
                        if type(resp_json) == list:
                            print "-->job_id: %s resp: [%s]" % (job_id, ', '.join(map(str, resp_json['data'])))
                        print "-->job_id: %s resp: [%s]" % (job_id, str(resp_json['data']))
                        self.redisconn.delete("*:" + job_id + ":*")
                        self.end_job_list.remove(end_job)
                        break 
                    
                    time.sleep(self.timeout_get_resp)
            
            if len(self.jobs_list)==0:
                break
            if len(self.end_job_list)==0:
                break
                        
            time.sleep(0.1)
        
if __name__ == "__main__":
    ctest= ExeSysTest()
    
    # -- create n single jobs
    for i in range(1,100):
        u= 'http://127.0.0.1:5000/exesyscmds'
        h= ctest.set_headers('single')
        p= ctest.set_payload( 'testclient', 
                              'end_job',
                              'test_cmd',
                              [i,0],
                              str(ctest.set_job_uuid()) )
        
        ctest.set_job(u, p, h)
    
    ctest.running = True
    ctest.run()
    
