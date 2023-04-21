from http.server import BaseHTTPRequestHandler


class HTTPServerRH(BaseHTTPRequestHandler):

    def doGET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        message = ''
        self.wfile.write(message, 'utf-8')
        return

    def doPOST(self):
        contentLength = int(self.headers['Content-Length'])
        postData = self.rfile.read(contentLength)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("", 'utf-8')