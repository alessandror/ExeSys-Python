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

import time
import subprocess
import os
import sys
import signal
from sys import platform as _platform

import redis

import environment as env


class ExeSysBootstrap():    
    
    def __init__(self): 
        self.redis_connect()
        self.start_delay =  0.2
        self.tika_pid_server_list = []
        
    def redis_connect(self):
        self.pool = redis.ConnectionPool(host=env.REDISIP, port=env.REDISPORT, db=env.REDISSYSDB)
        self.redis = redis.Redis(connection_pool=self.pool)
        
    def base_system(self): 

#redis
        print ">>>>>>> starting exe sys... press ctrl+C to stop"
        print ">>> starting redis"
        if _platform == "linux" or _platform == "linux2":
        # linux
            self.redis_srv='redis-server-linux'
        elif _platform == "darwin":
        # OS X
            self.redis_srv='redis-server-mac'
        elif _platform == "win32":
        # Windows...
            pass
        cmd = os.getcwd() + "/" + self.redis_srv + ' ' \
                          + os.getcwd() + '/redis.conf ' \
                          + '--port ' + str(env.REDISPORT)
        print ">>> CMD: ",cmd
        self.redis_server = subprocess.Popen(  cmd.split() , shell=False)
        print ">>> redis started"
        time.sleep(self.start_delay)
        print ">>> reset redis"
        self.redis.flushall()

#workers       
        print ">>> start workers"
        self.worker_pid_list =[]
        for worker_num in range(env.MAXWORKER):
            print "---> start worker #" + str(worker_num)
            worker = subprocess.Popen(['python', os.getcwd() + '/worker.py', '-w '+ str(worker_num)], shell=False)
            self.worker_pid_list.append(worker.pid)
            time.sleep(self.start_delay)

#webserver
        print ">>> start webserver"
        print os.getcwd()
        web_server = subprocess.Popen(['python', os.getcwd() + '/webserver.py'], shell=False)
        self.web_server_pid = web_server.pid
        time.sleep(self.start_delay)                

#rest server        
        print ">>> start rest server"
        print os.getcwd()
        rest_server = subprocess.Popen(['python', os.getcwd() + '/restserver.py'], shell=False)
        self.rest_server_pid = rest_server.pid
        time.sleep(self.start_delay)

#controller
        print ">>> start controller"
        print os.getcwd()
        controller= subprocess.Popen(['python', os.getcwd() + '/controller.py'], shell=False)
        self.controller_pid = controller.pid
        time.sleep(self.start_delay)
                
    def get_redis_pid(self):
        return self.redis_server_pid
    
    def get_worker_pid_list(self):
        return self.worker_pid_list

    def get_restserver_pid(self):
        return self.rest_server_pid

    def get_webserver_pid(self):
        return self.web_server_pid

    def get_controller_pid(self):
        return self.web_server_pid   

def signal_handler(a,b):
    print ">>> received ctrl+C"
    for i in  t.get_worker_pid_list():
        os.system('kill %s' % str(i))
        print ">>> stopped worker pid:%s" %(i.pid)
    os.system('kill %s' % t.get_webserver_pid())
    print ">>> stopped webserver pid:%s" %(t.get_webserver_pid())
    os.system('kill %s' % t.get_controller_pid())
    print ">>> stopped controller pid:%s" %(t.get_controller_pid())
    time.sleep(2)
    
    os.system('kill %s' % str(t.get_redis_pid()+1))
    print "redis_pid: %d" % t.get_redis_pid()
    print ">>>>>>> sys exe ends..."
    sys.exit()
    
if __name__ == '__main__':   
    signal.signal(signal.SIGINT, signal_handler)
    t= ExeSysBootstrap()
    t.base_system()

    while True:
        time.sleep(0.1)
        #print "looooping"

        


