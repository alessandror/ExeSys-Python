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

from ExeSysMain import environment as env

pool = redis.ConnectionPool(host=env.REDISIP, port=env.REDISPORT, db=env.REDISDATADB)
redisconn = redis.Redis(connection_pool=pool)

if __name__ == '__main__':
    '''import in redis dictionary from dbpedia interlanguage file '''
    
    with open("/Users/alexr/Downloads/interlanguage_links_en.ttl") as f:
        header_line = next(f) #skip first line
        for line in f:
            triples =  line.split()
            if triples[0]=='#':
                break
            a=b=c=None
            for index,i in enumerate(triples):
                i = i.replace("http://",'')
                i = i.replace('<','')
                i = i.replace('>','')
                i = i.split('/')
            
                if index == 0:
                    a= i[2]
                if index == 2:
                    b= i[0].split('.')[0]
                    c= i[2]
                if a and b and c != None:
                    #print a,b,c
                    key= 'wikt:' + c + ':' + b 
                    redisconn.set(key,a)
                    a=b=c=None
             
            