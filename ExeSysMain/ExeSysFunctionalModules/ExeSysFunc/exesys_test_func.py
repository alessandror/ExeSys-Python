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
import random

import redis

import ExeSysMain.environment as env

pool = redis.ConnectionPool(host=env.REDISIP, port=env.REDISPORT, db=env.REDISDATADB)
redisconn = redis.Redis(connection_pool=pool)


def test_error_cmd(data_to_process):
    resp = {}
    #print "test function with data %s" %  data_to_process
    time.sleep(2 * random.random())
    print str(1/0) 
    resp['EOJ'] = data_to_process
    return resp


def test_cmd(data_to_process):
    resp = {}
    #print "test function with data %s" %  data_to_process
    time.sleep(2 * random.random()) 
    resp['EOJ'] = data_to_process
    return resp


def test_cmd_workflow(data_to_process):
    resp = {}
    #print "test function with data %s" %  data_to_process
    time.sleep(2 * random.random())
    data_to_process[1]=data_to_process[1]+1
    resp['EOJ'] = data_to_process
    return resp


def test_cmd_workflow_1(data_to_process):
    resp = {}
    #print "test function with data %s" %  data_to_process
    #time.sleep(2 * random.random())
    key = 'workflow_test_key:' + str(data_to_process[0])
    data = redisconn.hget(key,
                   'text_data')
    if data:
        idata = float(data)
        idata = idata + 1.0
        data = str(idata)
        
        redisconn.hset(key,
                       'text_data',
                       data.encode('utf-8'))
        data_to_process[1]= data
    else:
        redisconn.hset(key,
                       'text_data',
                       '1'.encode('utf-8'))
    resp['EOJ'] = data_to_process
    return resp
