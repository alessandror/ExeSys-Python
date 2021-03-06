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
from ExeSysMain.ExeSysTest import base_test


sys.path.insert(0, os.path.join('', '../ExeSysMain') )

if __name__ == '__main__':
    ctest= base_test.ExeSysTest()
    
    for i in range(0,20):
        # -- get workflow id
        uuid= str(ctest.set_job_uuid())
        
        # -- workflow step 0 - start
        u= 'http://' + env.RSERVERIP + ':' + str(env.RSERVERPORT) + '/exesyscmds'
        h= ctest.set_headers('single')
        p= ctest.set_payload('step0', 'step1', 'test_cmd_workflow_1', [i,0], uuid )
        ctest.set_job(u, p, h)
        
        # -- workflow step 1
        u= 'http://' + env.RSERVERIP + ':' + str(env.RSERVERPORT) + '/exesyscmds'
        h= ctest.set_headers('workflow')
        p= ctest.set_payload('step1', 'step2', 'test_cmd_workflow_1', [i,0], uuid )
        ctest.set_job(u, p, h)
        
        # -- workflow step 2 - final
        u= 'http://' + env.RSERVERIP + ':' + str(env.RSERVERPORT) + '/exesyscmds'
        h= ctest.set_headers('workflow')
        p= ctest.set_payload('step2', 'end_job', 'test_cmd_workflow_1', [i,0], uuid )
        ctest.set_job(u, p, h)

    ctest.RUNTYPE=ctest.RUNWORKFLOW
    ctest.running = True
    ctest.run()