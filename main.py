#!/usr/bin/env python3
"""
Ultra-simple test server for debugging Coolify deployment
"""

import os
import http.server
import socketserver

PORT = int(os.getenv('PORT', 8002))

class TestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response = f"""
            <html>
            <head><title>Enhanced OSINT System v2.0</title></head>
            <body>
                <h1>🚀 Enhanced OSINT System v2.0</h1>
                <p>Status: <strong>Running</strong></p>
                <p>Port: {PORT}</p>
                <p>Environment: {os.getenv('ENVIRONMENT', 'production')}</p>
                <hr>
                <h2>Test Endpoints:</h2>
                <ul>
                    <li><a href="/health">/health</a> - Health check</li>
                    <li><a href="/status">/status</a> - Status info</li>
                </ul>
            </body>
            </html>
            """
            self.wfile.write(response.encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = '{"status": "healthy", "message": "Server is running"}'
            self.wfile.write(response.encode())
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = '{"status": "idle", "port": ' + str(PORT) + '}'
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

if __name__ == '__main__':
    print(f"🚀 Starting Enhanced OSINT System test server on port {PORT}")
    with socketserver.TCPServer(("", PORT), TestHandler) as httpd:
        print(f"✅ Server started successfully on port {PORT}")
        print(f"🌐 Access at: http://localhost:{PORT}")
        httpd.serve_forever()