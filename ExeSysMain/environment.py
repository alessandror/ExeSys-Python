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

#REST SERVER PORT
RSERVERIP='127.0.0.1'
RSERVERPORT=50000

#WEBSERVERPORT
WEBSERVERPORT='127.0.0.1'
WEBSERVERPORT=50001

#LOGGING 
LOGGING = 1

#DEBUGGING
DEBUG_DATA_AVAILABLE=False

#FUNCTION MODULE
# FUNCT_MODULE='ExeSysFunctionalModules.IR'
# FUNCT='text_processing_functions'

FUNCT_MODULE='ExeSysFunctionalModules.ExeSysFunc'
FUNCT='exesys_test_func'

#WORKER QUEUE PARAM
MAXWORKER = 3

#REDIS MAIN SERVER
REDISIP     = '127.0.0.1'
REDISPORT   = 6380
REDISSYSDB  = 0
REDISDATADB = 1
REDISDATASERVERDB = 2
REDISRUNNERDB = 3

#WORD DICT SERVER
WDIP = '127.0.0.1'
WDPORT = 6381