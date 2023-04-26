import json
from http.server import BaseHTTPRequestHandler


class HTTPServerRH(BaseHTTPRequestHandler):
    status = "waiting"

    def do_GET(self):
        if self.path == "/status":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            message = {"status": self.status}
            self.wfile.write(json.dumps(message).encode('utf-8'))
            return

    def do_POST(self):
        if self.path == "/get":
            contentLength = int(self.headers['Content-Length'])
            postData = self.rfile.read(contentLength).decode("utf-8")
            req = json.loads(postData)
            self.status = "http request"
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            message = {"status": self.status}
            self.wfile.write(json.dumps(message).encode('utf-8'))
            return
