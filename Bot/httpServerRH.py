import json
import platform
import psutil
from http.server import BaseHTTPRequestHandler

import requests


def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def doRequest(url, time):
    for i in range(time):
        try:
            print("Doing request at ", url)
            response = requests.get(url)
        except Exception as e:
            print("Request error: ", e)


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
        elif self.path == "/getSystemInfo":
            self.status = "waiting"
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            try:
                uname = platform.uname()
                svmem = psutil.virtual_memory()
                partition = psutil.disk_partitions()
                message = {
                    "System": uname.system,
                    "Node name": uname.node,
                    "Release": uname.release,
                    "Version": uname.version,
                    "Machine": uname.machine,
                    "Processor": platform.processor(),
                    "Physical cores": psutil.cpu_count(logical=False),
                    "Total cores": psutil.cpu_count(logical=True),
                    "Memory": get_size(svmem.total),
                }
                self.wfile.write(json.dumps(message).encode('utf-8'))
            except Exception as e:
                print(e)
                pass
            return

    def do_POST(self):
        if self.path == "/doGet":
            contentLength = int(self.headers['Content-Length'])
            postData = self.rfile.read(contentLength).decode("utf-8")
            req = json.loads(postData)
            self.status = "executing http request"
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            message = {"status": self.status}
            self.wfile.write(json.dumps(message).encode('utf-8'))
            doRequest(req["url"], int(req["time"]))
            return

