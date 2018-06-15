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

import os
import subprocess
import time

import redis

import environment as env


class WordDict():
    def __init__(self):
        pool = redis.ConnectionPool(host=env.WDIP, port=env.WDPORT, db=0)
        self.redisconn = redis.Redis(connection_pool=pool)
        self.redis_server_pid=0

    def start_word_dict_server(self):
        print "-> starting exe sys... press ctrl+C to stop"
        print "-> starting redis"
        print os.getcwd()
        cmd = os.getcwd() + '/redis-server ' \
                          + os.getcwd() + '/redis-word-dict.conf ' \
                          + '--port ' + str(env.WDPORT)
        print cmd                    
        redis_server = subprocess.Popen( cmd.split(), shell=False)
        self.redis_server_pid = redis_server.pid
        print "-> redis started : %d" % self.redis_server_pid
    
    def get_redis_pid(self):
        return self.redis_server_pid
     
if __name__ == '__main__':
    s = WordDict()
    s.start_word_dict_server()
    try:
        while 1:
            time.sleep(0.1)      
    except KeyboardInterrupt: 
        os.system('kill %s' % str(s.get_redis_pid()+1)) 


       
