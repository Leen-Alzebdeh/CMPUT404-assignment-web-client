#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        if port is None or port == '': 
            port = 80
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return self.parse_request()[0]

    def get_headers(self,data):
        return self.parse_request()[1]

    def get_body(self, data):
        return self.parse_request()[2]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    def parse_request(self, req):
        url = ''
        headers = {}
        lines = req.splitlines()
        inbody = False
        body = ''
        for line in lines[1:]:
            if line.strip() == "":
                inbody = True
            if inbody:
                body += line
            else:
                k, v = line.split(":", 1)
                headers[k.strip()] = v.strip()
        code = int(lines[0].split()[1])
        return code, headers, body

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        request = ""
        o = urllib.parse.urlparse(url)
        hostname, port, path = o.hostname, o.port, o.path
        print(hostname, port, path)
        self.connect(hostname, port)
        query = ""
        if args is not None: query = query = "?" + urllib.parse.urlencode(args)
        if path == "" or path is None: 
            path = "/"
            print("inside if")
            request = "GET " + path + " HTTP/1.1\r\nHost: "+ hostname + "\r\nAccept: text/html;charset=utf-8,*/*;charset=utf-8\r\nAccept-Charset: UTF-8\r\n\r\n"
            self.sendall(request)
            response = "HTTP/1.1 301 Moved Permanently\r\nLocation: " + hostname + path + "\r\n\r\n"
        else: 
            self.sendall("GET " + path + query + " HTTP/1.1\r\nHost: "+ hostname + "\r\nAccept: text/html;charset=utf-8,*/*;charset=utf-8\r\nAccept-Charset: UTF-8\r\n\r\n")
            response = self.recvall(self.socket)
        print(response) 
        code, headers, body = self.parse_request(response)
        
        return HTTPResponse(code, body)    

    def POST(self, url, args=None):
        code = 500
        body = ""
        o = urllib.parse.urlparse(url)
        hostname, port, path, query = o.hostname, o.port, o.path, o.query
        self.connect(hostname, port)
        query = ""
        if args is not None: query = query = urllib.parse.urlencode(args)
        length = str(len(query))
        self.sendall("POST " + path + " HTTP/1.1\r\nHost: "+ hostname + "\r\nAccept: text/html;charset=utf-8,*/*;charset=utf-8\r\nAccept-Charset: UTF-8\r\nContent-Length:" + length + "\r\n\r\n" + query)
        response = self.recvall(self.socket)
        print(response) 
        code, headers, body = self.parse_request(response)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
