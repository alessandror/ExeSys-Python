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
import signal
import time
import sys

import messenger as msgr
import environment as env


class Controller(threading.Thread):
    """base system controller"""

    def __init__(self, elapsed_time,f):
        self.elapsed_time = elapsed_time
        self.stopped = threading.Event()
        self.f = f
        threading.Thread.__init__(self)

    def stop(self):
        self.stopped.set()
        
    def run(self):
        while not self.stopped.is_set():
            self.f()
            self.stopped.wait(self.elapsed_time)

#------- CONTROLLER FUNCTIONS
def build_and_exe_post_to_rest_server(cmd):
    csysmsg = msgr.ExeSysMsg( env.REDISIP, \
                              env.REDISPORT, \
                              env.REDISSYSDB)
    u= 'http://127.0.0.1:'+ str(env.RSERVERPORT) +'/exesyscmds'
    h= csysmsg.set_headers('single')
    p= csysmsg.set_payload('testclient', \
                         'end_job', \
                         'telecom_api_wrapper_cmd', \
                          ['redis',  cmd], \
                          str(csysmsg.set_job_uuid()) )
        
    csysmsg.set_job(u, p, h)
        
    csysmsg.RUNTYPE=csysmsg.RUNSINGLE
    csysmsg.running = True
    csysmsg.run()
    rsp=  csysmsg.get_current_resp()
    return rsp

def update_system_configuration():
    #print "\n update system configuration get hgw id"
    resp = build_and_exe_post_to_rest_server('get_hgw_id')
    #print "\gateway id response: %s" % resp

    #print "\n update system configuration get system configuration"
    resp = build_and_exe_post_to_rest_server('get_device_list')
    #print "\get device list resp: %s" % resp

def update_devices_status():
    #print "\n update system configuration get hgw id"
    resp = build_and_exe_post_to_rest_server('get_hgw_id')
    #print "\gateway id response: %s" % resp

    #print "\n update system devices status"
    resp = build_and_exe_post_to_rest_server('get_all_device_status')
    #print "\update system devices status resp: %s" % resp

def signal_handler(a,b):
    print "received ctrl+C"
    sys.exit()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    # sysconfig_updater = Controller(5, update_system_configuration)
    # sysconfig_updater.start()

    # sys_devs_status_updater = Controller(5, update_devices_status)
    # sys_devs_status_updater.start()

    while True:
        time.sleep(0.1)

