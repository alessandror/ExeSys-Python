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
from os.path import expanduser

from ExeSysMain import environment as env
from ExeSysMain.ExeSysTest import base_test


user_home = expanduser("~")

import sys,os
sys.path.insert(0, os.path.join('', '../ExeSysMain') )

if __name__ == '__main__':

    ctest= base_test.ExeSysTest()
    
    # -- create n single jobs
#     for i in range(1,4):
#         u= 'http://127.0.0.1:5000/exesyscmds'
#         h= ctest.set_headers('single')
#         p= ctest.set_payload('testclient', \
#                              'end_job', \
#                              'tika_read_document', \
#                               ['filesys-folder', \
#                                '/Users/alexr/test_docs/test_folder_'+str(i)+'/'],\
#                               str(ctest.set_job_uuid()) )
#         
#         ctest.set_job(u, p, h)
    
    
    # -- test import document from folder 
    u= 'http://' + env.RSERVERIP + ':' + str(env.RSERVERPORT) + '/exesyscmds'
    h= ctest.set_headers('single')
    p= ctest.set_payload('testclient', \
                             'end_job', \
                             'tika_read_document', \
                              ['filesys-folder', \
                               user_home + '/test_docs/5k_0/'],\
                              str(ctest.set_job_uuid()) )    
        
    ctest.set_job(u, p, h)     
    
    ctest.RUNTYPE=ctest.RUNSINGLE
    ctest.running = True
    ctest.run()