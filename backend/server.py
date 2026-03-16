#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import urllib.request
import urllib.error
import json
import os
import socket

CLASH_API = os.environ.get('CLASH_API_URL', 'http://127.0.0.1:9090')

class ProxyHandler(SimpleHTTPRequestHandler):
    extensions_map = {
        '.html': 'text/html', '.css': 'text/css', '.js': 'application/javascript',
        '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg',
        '.ico': 'image/x-icon', '': 'text/html',
    }
    
    def log_message(self, format, *args):
        pass
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Connection', 'close')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        try:
            if self.path.startswith('/api/'):
                self.proxy_to_clash('GET')
            else:
                if self.path == '/':
                    self.path = '/index.html'
                super().do_GET()
        except Exception as e:
            self.send_error(500, str(e))
    
    def do_PUT(self):
        try:
            if self.path.startswith('/api/'):
                self.proxy_to_clash('PUT')
            else:
                self.send_error(404)
        except Exception as e:
            self.send_error(500, str(e))
    
    def proxy_to_clash(self, method):
        try:
            path = self.path.replace('/api', '', 1)
            url = f'{CLASH_API}{path}'
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            req = urllib.request.Request(url, data=body, method=method)
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Connection', 'close')
                self.end_headers()
                self.wfile.write(data)
        except Exception as e:
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

if __name__ == '__main__':
    port = 9093
    socket.TCP_NODELAY = 1
    print(f'Starting ThreadingHTTPServer on port {port}, API: {CLASH_API}')
    server = ThreadingHTTPServer(('0.0.0.0', port), ProxyHandler)
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    server.serve_forever()
