#!/usr/bin/python

"""
This server allow you to serve the static content from the folder of your choice below the root of the this script.
Then every request that contains a key word like "/rest" will be forwarded to another server (Application Server for instance)

Browser ---> Python HTTP server ---> Static content
                                \
                                  --> Application Server (localhost on different port)
"""

import SimpleHTTPServer
import SocketServer
import logging
import cgi

import urlparse
import urllib
import urllib2

import argparse
import sys

APPLICATION_SERVER = 'http://ncmt1.dev.amadeus.net'
ROUTING_KEY_WORD = '/cmt/apf'

CRITICAL=50
ERROR=40
WARNING=30
INFO=20
DEBUG=10
NOTSET=0

parser = argparse.ArgumentParser(usage="%(prog)s -s serverurl -r path [--log LOG] [-p PORT]")
parser.add_argument('--log', type=int, choices=['CRITICAL', 'ERROR', 'WARNING','INFO','DEBUG'], default=WARNING, help='Set the level of log for the logging facility')
parser.add_argument('-s', metavar="serverurl",  help='The url to forward the request to (ie:http://www.myproduction.com)')
parser.add_argument('-r', metavar="path", help='The identifier inside the url that trigger the forward the request to (ie:/rest/)')
parser.add_argument('-p', metavar="PORT", type=int, default=8000, help='To run on a dedicated port when the port 8000 is used')
parser.add_argument('-d', metavar="DEBUG",choices=['False', 'True'],  default=False, help='To run in debug mode, with more log, with a proxy on port 8080')
args = parser.parse_args()

if args.r == None or args.s==None:
    parser.print_help()
    sys.exit(1)

APPLICATION_SERVER = args.s
ROUTING_KEY_WORD = args.r
PORT = args.p
I=""
debug=args.d

logging.basicConfig(level=args.log)
    
class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        global APPLICATION_SERVER
        logging.info("======= GET Request =======")
        logging.info(self.path)
        if self.path.startswith(ROUTING_KEY_WORD):
            url = APPLICATION_SERVER+self.path
            request = urllib2.Request(url)
            self.processRequest(request,url);
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        global APPLICATION_SERVER
        logging.info("======= POST Request =======")
        postvars = self.parse_POST()
        if self.path.startswith(ROUTING_KEY_WORD):
            url = APPLICATION_SERVER+self.path
            data = postvars.iterkeys().next();
            logging.info(postvars[data][0]);
            request = urllib2.Request(url,data+"="+str(postvars[data][0]))
            self.processRequest(request,url);
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_POST(self)
            
    def processRequest(self, request,url):
        self.forward_header(request);
        if debug:
            request.set_proxy("127.0.0.1:8080","http")
        print "%(baseurl)s forwarded to %(forwardurl)s" % dict(baseurl=self.path,forwardurl=url)
        response = urllib2.urlopen(request)
        body = response.read()
        self.send_response(200)
        self.forward_reply_header(response)
        self.wfile.write(body)
    
    def forward_reply_header(self,response):
        self.send_header("Content-type", response.info().getheader('Content-Type'))
        self.send_header("Set-Cookie", response.info().getheader('Set-Cookie'))
        self.end_headers()
    
    def forward_header(self,reqout):
        if debug:
            print self.headers
        for key in self.headers.keys():
            reqout.add_header(key, self.headers[key])

    def parse_POST(self):
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        logging.debug('Content Type:'+ctype);
        if ctype == 'multipart/form-data':
            logging.debug('multipart/form-data');
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            logging.debug('application/x-www-form-urlencoded');
            length = int(self.headers['content-length'])
            postvars = cgi.parse_qs(
                    self.rfile.read(length), 
                    keep_blank_values=1)
        elif ctype == 'application/json':
            logging.debug('application/json');
            length = int(self.headers['content-length'])
            postvars = cgi.parse_qs(
                    self.rfile.read(length), 
                    keep_blank_values=1)
        else:
            postvars = {}
        return postvars
            
Handler = ServerHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "Python http server version 0.3 (for testing purposes only)"
print "Serving at: http://%(interface)s:%(port)s" % dict(interface=I or "localhost", port=PORT)
print "Forwarding to: %(AS)s request containing: %(filter)s" % dict(AS=APPLICATION_SERVER,filter=ROUTING_KEY_WORD)
print "ctrl-c to close"
httpd.serve_forever()
