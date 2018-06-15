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

import sys
import os

from ExeSysMain import environment as env

sys.path.insert(0, os.path.join("..", "../ExeSysMain/") )

import redis

if __name__ == '__main__':
    pool = redis.ConnectionPool(host=env.WDIP, port=env.WDPORT, db=0)
    redisconn = redis.Redis(connection_pool=pool)
    
    file_to_parse= ''
    
    with open("./word_pairs") as f:
        num= 0 
        for line in f:
            split_line = line.split("\t")
            en_word = it_word = ''
            if 'en' in split_line[0]:
                en_word = split_line[1]
            if 'it' in split_line[2]:
                it_word = split_line[3]
                
            if en_word != '' and it_word != '':
                print "%d  %s <-> %s" % (num,en_word.replace(" ","_"),it_word.replace(" ","_"))
                num = num +1
