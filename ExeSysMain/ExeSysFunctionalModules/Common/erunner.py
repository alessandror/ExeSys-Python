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
import time
import redis
import ExeSysMain.environment as env

class Runner(threading.Thread):

    def __init__(self,classref,type,uuid,
                 redis_ip=env.REDISIP,
                 redis_port=env.REDISPORT,
                 redis_db=env.REDISRUNNERDB):
        self.redis_ip = redis_ip
        self.redis_port = redis_port
        self.redis_runner_db = redis_db
        self.enable = True
        self.ref_class = classref
        self.type = type
        self.uuid = uuid
        self.redis_connect()
        super(Runner, self).__init__()

    def redis_connect(self):
        self.pool = redis.ConnectionPool(host=self.redis_ip,
                                         port=self.redis_port,
                                         db=self.redis_runner_db)
        self.redis_runner_conn = redis.Redis(connection_pool=self.pool)

    def stop(self):
        self.enable = False

    def run(self, delay=0.100):
        while self.enable:

            runner_status = self.redis_runner_conn.get("run:" +
                                                       self.type +
                                                       ":" +
                                                       self.uuid)
            print "--> Runner Status: %s" % runner_status
            if '0' in runner_status:
                ret = self.ref_class.stop_collecting()
                print "--->END RUNNER: %s" % ret
                break
            time.sleep(delay)

