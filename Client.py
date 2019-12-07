from threading import *
import time
import pickle
from socket import *
import utilities

class Client:
    
    def __init__(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.watchers = []

        with open("port.txt", "r") as f:   
            self.port = int(f.readline())

        self.sock.connect(('localhost', self.port))
        self._login = False
        self.terminate= False
        self.socks = []
        self.lock = Lock()

    def register(self, email, namesurname, password, balance):
        self.sock.send(pickle.dumps({"type":"register",
                        "email": email,
                        "namesurname": namesurname, 
                        "password": password, 
                        "balance": balance}))
        while True:
            resp = pickle.loads(self.sock.recv(1000))
            print(resp)
            if resp["type"] == "message" and resp["message"] == "OK":
                self._login = True
                self.email = email
                self.password = password
                break
    
    def close(self):
        self.terminate = True
        self.sock.send(pickle.dumps({"type":"close"}))
        for i in self.socks:
            i.send(pickle.dumps({"type": "close_"}))
            i.close()
        while True:
            resp = pickle.loads(self.sock.recv(1000))
            print(resp)
            if resp["type"] == "message":
                self._login = False
                break

        print("closed")
        self.sock.close()
    
    def login(self, email, password):
        self.sock.send(pickle.dumps({"type":"login",
                        "email": email,
                        "password": password}))
        while True:
            resp = pickle.loads(self.sock.recv(1000))
            print(resp)
            if resp["type"] == "message":
                if resp["message"] == "OK":
                    self._login = True
                    self.email = email
                    self.password = password
                break

    def verify(self):
        verf = utilities.verf(self.email)
        self.sock.send(pickle.dumps({"type":"user", 
                        "operation": "verify", 
                        "verification_number": verf}))
        while True:
            resp = pickle.loads(self.sock.recv(1000))
            print(resp)
            if resp["type"] == "message":
                break

    def change_password(self, new_password, old_password):
        self.sock.send(pickle.dumps({"type":"user", 
                        "operation": "change_password", 
                        "new_password": new_password,
                        "old_password": old_password}))

        while True:
            resp = pickle.loads(self.sock.recv(1000))
            print(resp)
            if resp["type"] == "message":
                break
    
    def list_items(self, email, item_type, state):
        self.sock.send(pickle.dumps({"type":"user", 
                        "operation": "listitems", 
                        "email": email,
                        "item_type": item_type,
                        "state": state}))

        while True:
            resp = pickle.loads(self.sock.recv(1000))
            print(resp)
            if resp["type"] == "message":
                break

    def report(self):
        self.sock.send(pickle.dumps({"type":"user", 
                        "operation": "report"}))

        while True:
            resp = pickle.loads(self.sock.recv(1000))
            print(resp)
            if resp["type"] == "message":
                break
    
    def sell_item(self, title):
        self.sock.send(pickle.dumps({"type":"user", 
                        "operation": "sell_item", 
                        "title": title}))

        while True:
            resp = pickle.loads(self.sock.recv(1000))
            print(resp)
            if resp["type"] == "message":
                break

    def create_item(self, title, itemtype, description, auction_type,
                    starting, minbid=1.0, image=None):

        self.sock.send(pickle.dumps({"type":"sell_item",
                                "operation": "create_item",
                                "title": title,
                                "itemtype": itemtype,
                                "description": description,
                                "auction_type": auction_type,
                                "starting": starting,
                                "minbid": minbid,
                                "image": image}))

        while True:
            resp = pickle.loads(self.sock.recv(1000))
            print(resp)
            if resp["type"] == "message":
                break

    def start_auction(self, title):
        self.sock.send(pickle.dumps({"type":"sell_item",
                        "operation": "start_auction",
                        "title": title}))

        while True:
            resp = pickle.loads(self.sock.recv(1000))
            print(resp)
            if resp["type"] == "message":
                break
    def bid(self, title, amount):
        self.sock.send(pickle.dumps({"type":"sell_item", 
                        "operation": "bid", 
                        "title": title,
                        "amount": amount}))
        
        while True:
            resp = pickle.loads(self.sock.recv(1000))
            print(resp)
            if resp["type"] == "message":
                break

    def sell(self, title):
        self.sock.send(pickle.dumps({"type":"sell_item",
                        "operation": "sell",
                        "title": title}))
        
        while True:
            resp = pickle.loads(self.sock.recv(1000))
            print(resp)
            if resp["type"] == "message":
                break
    
    def view(self, title):
        self.sock.send(pickle.dumps({"type":"sell_item",
                        "operation": "view",
                        "title": title}))

        while True:
            resp = pickle.loads(self.sock.recv(1000))
            print(resp)
            if resp["type"] == "message":
                break

    def history(self, title):
        self.sock.send(pickle.dumps({"type":"sell_item",
                        "operation": "history",
                        "title": title}))

        while True:
            resp = pickle.loads(self.sock.recv(1000))
            print(resp)
            if resp["type"] == "message":
                break

    def notification_thread(self, title=None, email=None, itemtype=None):
        notf_sock = socket(AF_INET, SOCK_STREAM)
        notf_sock.connect(('localhost', self.port))
        notf_sock.settimeout(1)
        with self.lock:
            self.socks.append(notf_sock)
        if itemtype == None:
            notf_sock.send(pickle.dumps({"type":"sell_item",
                        "operation": "watch",
                        "title": title,
                        "email": email}))
        else:
            notf_sock.send(pickle.dumps({
                "type": "user",
                "operation": "watch_user",
                "itemtype": itemtype
            }))
        while not self.terminate:
            try:
                resp = notf_sock.recv(1000)
                print("notification to {}".format(self.email) , pickle.loads(resp))
            except:
                pass

    def watch(self, title):
        t = Thread(target=self.notification_thread, args=(title, self.email,))
        t.start()
        self.watchers.append(t)

    def watch_user(self, itemtype):
        t = Thread(target=self.notification_thread, args=(None,None,itemtype,))
        t.start()
        self.watchers.append(t)