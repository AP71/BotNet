import json
from http.server import BaseHTTPRequestHandler


class HTTPServerRH(BaseHTTPRequestHandler):

    status = "waiting"

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        message = { "status": self.status}
        self.wfile.write(json.dumps(message).encode('utf-8'))
        return

    def do_POST(self):
        contentLength = int(self.headers['Content-Length'])
        postData = self.rfile.read(contentLength)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("", 'utf-8')