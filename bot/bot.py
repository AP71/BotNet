import socket

class Bot:
    host = '127.0.0.1'
    port = 49171
    status = ''
    ports = [41199]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self):
        self.sendInfo()
        self.status = 'waiting'
        self.listen()

    def sendInfo(self):
        try:
            self.s.connect((self.host, self.port))
            message = socket.gethostbyname(socket.gethostname()) + " " + self.ports.__str__()
            while message != 'bot registrated succesfully':
                self.s.send(message.encode())
                message = self.s.recv(1024).decode()
            self.s.close()
        except:
            print("Information send error")
        finally:
            self.s.close()

    def listen(self):
        try:
            self.s.bind(('', self.ports[0]))
            while (True):
                self.s.listen()
                conn, addr = self.s.accept()
                data = conn.recv(1024).decode()
                data = data.split(" ")
                print(data)
                conn.close()
        except:
            print("Listening error")
        finally:
            self.s.close()


if __name__ == '__main__':
    b = Bot()