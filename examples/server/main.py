import argparse
import json
import http.server

# Hack to inport wfc module here
# ASSUMES that you are running this file from its parent directory, i.e python examples/file.py
import os
import sys
if os.getcwd() not in sys.path: sys.path.append(os.getcwd())

class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try: data = json.loads(post_data)
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "error", "message": "Invalid JSON"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        res = self.handle_post_request(data)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(res).encode('utf-8'))
    
    def handle_post_request(self, data):
        print("Data received:", data)
        response = {
            "status": "success",
            "data": data
        }
        return response

def run(server_class=http.server.HTTPServer, handler_class=Handler, port=5555):
    server_address = ('', port) # Hosts at local host
    httpd = server_class(server_address, handler_class)
    print(f'Starting server at http://localhost:{port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, help="Server's port. defaults to 5555")
    args = parser.parse_args()

    if args.port: run(port = args.port)
    else: run()