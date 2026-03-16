#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error
import json
import yaml
import os
import threading

CLASH_API = 'http://127.0.0.1:9090'
CONFIG_PATH = '/opt/clash/config.yaml'

class APIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/api/proxies':
            self.proxy_clash('/proxies')
        elif self.path == '/api/configs':
            self.proxy_clash('/configs')
        elif self.path == '/api/traffic':
            self.proxy_clash('/traffic')
        elif self.path == '/api/providers':
            self.get_providers()
        else:
            self.send_error(404)
    
    def do_PUT(self):
        if self.path.startswith('/api/proxies/'):
            group = self.path.split('/')[-2]
            self.proxy_clash(f'/proxies/{group}', 'PUT')
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/add-provider':
            self.add_provider()
        elif self.path == '/api/remove-provider':
            self.remove_provider()
        else:
            self.send_error(404)
    
    def proxy_clash(self, path, method='GET'):
        try:
            url = f'{CLASH_API}{path}'
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            req = urllib.request.Request(url, data=body, method=method)
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(data)
        except Exception as e:
            self.send_response(503)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def get_providers(self):
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = yaml.safe_load(f)
            providers = config.get('proxy-providers', {})
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'proxyGroupProviders': list(providers.keys())}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def add_provider(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            name = data.get('name')
            url = data.get('url')
            
            if not name or not url:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': '名称和 URL 不能为空'}).encode())
                return
            
            with open(CONFIG_PATH, 'r') as f:
                config = yaml.safe_load(f)
            
            if 'proxy-providers' not in config:
                config['proxy-providers'] = {}
            
            config['proxy-providers'][name] = {
                'type': 'http',
                'url': url,
                'interval': 3600,
                'path': f'./{name}.yaml',
                'health-check': {
                    'enable': True,
                    'interval': 600,
                    'url': 'http://www.gstatic.com/generate_204'
                }
            }
            
            with open(CONFIG_PATH, 'w') as f:
                yaml.dump(config, f)
            
            # 重启 Clash
            os.system('systemctl restart clash')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def remove_provider(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            name = data.get('name')
            
            with open(CONFIG_PATH, 'r') as f:
                config = yaml.safe_load(f)
            
            if 'proxy-providers' in config and name in config['proxy-providers']:
                del config['proxy-providers'][name]
            
            with open(CONFIG_PATH, 'w') as f:
                yaml.dump(config, f)
            
            os.system('systemctl restart clash')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

if __name__ == '__main__':
    port = 9094
    print(f'Starting API server on port {port}')
    ThreadingHTTPServer.allow_reuse_address = True
    ThreadingHTTPServer(('0.0.0.0', port), APIHandler).serve_forever()
