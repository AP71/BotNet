import concurrent
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from concurrent.futures import ThreadPoolExecutor
from httpServerRH import HTTPServerRH
import ftpServer


class Bot:
    myIp = socket.gethostbyname(socket.gethostname())
    host = '127.0.0.1'
    port = 49171
    status = ''
    httpPort = 80
    ftpPort = 1111

    def __init__(self):
        self.sendInfo()
        self.status = 'waiting'
        task = []
        with ThreadPoolExecutor(max_workers=2) as exec:
            task.append(exec.submit(self.httpServer()))
            done, not_done = concurrent.futures.wait(task, return_when=concurrent.futures.FIRST_COMPLETED)
            exec.shutdown(wait=False)

    def sendInfo(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            message = self.myIp + ' {"http":' + str(self.httpPort) + ',"ftp":' + str(self.ftpPort) + ',"status":"waiting"}'
            while message != 'bot registrated succesfully':
                s.send(message.encode())
                message = s.recv(1024).decode()
            s.close()
        except Exception as e:
            print("Information send error: ", e)
        finally:
            s.close()

    def httpServer(self):
        try:
            httpd = HTTPServer((self.myIp, self.httpPort), HTTPServerRH)
            httpd.serve_forever()
        except Exception as e:
            print("HTTP error: ", e)

    def ftpServer(self):
        try:
            ftpServer.run(self.myIp, self.port)
        except Exception as e:
            print("FTP error: ", e)


if __name__ == '__main__':
    b = Bot()
