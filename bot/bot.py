import socket

class Bot:
    host = '127.0.0.1'
    port = 49171
    status = ''
    ports = [49199]
    def __init__(self):
        self.sendInfo()
        self.status = 'waiting'
        self.listen()

    def sendInfo(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            message = socket.gethostbyname(socket.gethostname()) + " " + self.ports.__str__()
            while message != 'bot registrated succesfully':
                s.send(message.encode())
                message = s.recv(1024).decode()
            s.close()
        except Exception as e:
            print("Information send error: ",e)
        finally:
            s.close()

    def listen(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', self.ports[0]))
            while (True):
                s.listen()
                conn, addr = s.accept()
                data = conn.recv(1024).decode()
                data = data.split(" ")
                print(data)
                conn.close()
        except Exception as e:
            print("Listening error: ",e)
        finally:
            s.close()


if __name__ == '__main__':
    b = Bot()