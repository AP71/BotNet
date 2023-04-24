import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

from httpServerRH import HTTPServerRH


class Bot:
    myIp = socket.gethostbyname(socket.gethostname())
    host = '127.0.0.1'
    port = 49171
    status = ''
    ports = [80, 1111, 9989]

    def __init__(self):
        self.sendInfo()
        self.status = 'waiting'
        self.listen()

    def sendInfo(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            message = self.myIp + " " + self.ports.__str__().replace(' ','')
            while message != 'bot registrated succesfully':
                s.send(message.encode())
                message = s.recv(1024).decode()
            s.close()
        except Exception as e:
            print("Information send error: ", e)
        finally:
            s.close()

    def listen(self):
        try:
            httpd = HTTPServer((self.myIp, self.ports[0]), HTTPServerRH)
            httpd.serve_forever()
        except Exception as e:
            print("HTTP error: ", e)


if __name__ == '__main__':
    b = Bot()
