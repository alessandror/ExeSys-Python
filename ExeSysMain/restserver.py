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

# -*- coding: utf-8 -*-

import cPickle
import json

import redis
from flask import Flask
from flask import request

import redis_scripts as rs
import environment as env


app = Flask(__name__)

pool = redis.ConnectionPool(host=env.REDISIP, port=env.REDISPORT, db=env.REDISSYSDB)
redisconn = redis.Redis(connection_pool=pool)

cmd_job_id = ""

@app.route('/exesyscmds', methods = ['POST'])
def api_message():
    """ get message, look if job is already in queue it and sends to supervisor """
    
    if request.headers['Content-Type'] == 'text/plain':
        return "Text Message: " + request.data

    elif request.headers['Content-Type'] == 'application/json':
        req = request.json
        #print "\n\n--> rest web server requested to process command %s" % (req)
        
        if 'Operation' in request.headers.keys():
            if request.headers['Operation'] == 'workflow':
                resp = command_processor(req,'STANDBY')
            return resp
       
        resp = command_processor(req,'NORMAL')

        return resp

    elif request.headers['Content-Type'] == 'application/octet-stream':
        f = open('./binary', 'wb')
        f.write(request.data)
        f.close()
        return "binary message processed"
    else:
        return "415 Unsupported Media Type"

@app.errorhandler(500)
def internal_error(error):
    ''' if error delete active job queue on jobid '''
    redisconn.hget("del","*:" + cmd_job_id + ":*")
    return "500 error caz!!"

@app.route('/notify', methods = ['POST'])
def notify_message():
    ''' receive notifications end point '''
    if request.headers['Content-Type'] == 'text/plain':
        return "Text Message: " + request.data
    
    elif request.headers['Content-Type'] == 'text/xml':
        return "xml processed"
    
    elif request.headers['Content-Type'] == 'application/json':
        req = request.json
        #print "--> rest web server process command: %s \n" % (req)
        resp = command_processor(req,'NORMAL')
        return resp

    elif request.headers['Content-Type'] == 'application/octet-stream':
        f = open('./binary', 'wb')
        f.write(request.data)
        f.close()
        return "binary message processed"
    else:
        return "415 Unsupported Media Type"


def command_processor(cmd,start_type):
    '''process rest commands
       start a process setting start status 
       process data_available status( if receives a request with same job_id and the status
         is data_available returns the data)
       process end_job status '''
    
    cmd_from = cmd['from']
    cmd_job_id = cmd['job_id']
    cmd_to = cmd['to']
    cmd_cmd = cmd['cmd']
    cmd_data = cmd['data']
    
    #print "-> vars %s %s  %s  %s  %s \n" % (cmd_from,cmd_job_id,cmd_to,cmd_cmd,cmd_data,start_type)
    #print "\n\n--> rest web server cmd processor new command - %s - : %s \n\n" % (start_type,cmd)
    script_resp = None
    while script_resp is None:
        script_resp = start_job_script(keys=["*:" + cmd_job_id + ":*"], args=[cmd_from,
                                                                              cmd_job_id,
                                                                              cmd_to,
                                                                              cmd_cmd,
                                                                              json.dumps(cmd_data),
                                                                              start_type])
        #time.sleep(0.05)
        
    if "data_available" in script_resp:
        
        result_to = redisconn.hget(cmd_from + ':' + cmd_job_id + ':' + 'data_available', 'to')

        if result_to == "end_job":
            result_data = redisconn.hget(cmd_from + ':' + cmd_job_id + ':' + 'data_available', 'result')
            
            unpickled_result = cPickle.loads(result_data)
            
            if not env.DEBUG_DATA_AVAILABLE:
                redisconn.delete(cmd_from + ':' + cmd_job_id + ':' + 'data_available')

            return '{\"resp\":\"data_available\"' + ',\"data\":' + json.dumps(unpickled_result) + '}'
    else: 
        return script_resp  
 
if __name__ == '__main__':
    start_job_script = redisconn.register_script(rs.rest_insert_new_job_and_check_status())
    import logging
    log=logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.debug = False
    app.run(port=env.RSERVERPORT)
