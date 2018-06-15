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

from flask import Flask
from flask import request,send_from_directory,Response

import environment as env


app = Flask(__name__, static_folder='./static')

def webserver():
    pass

@app.route('/<path:path>')
def static_serve(path):
    print ">>>>> web path: %s" % request.path
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/event_stream')
def stream():
    def event_stream():
        while True:
            time.sleep(3)
            yield 'data: %s\n\n' % 'test'
 
    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    
    app.debug = False
    app.run(host='0.0.0.0', port=env.WEBSERVERPORT)

 
