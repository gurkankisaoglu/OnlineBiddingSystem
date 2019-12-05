from threading import *
import json
import pickle
from User import User
from Sellitem import SellItem


class Agent(Thread):
    def __init__(self, ns, data_mutex, users):
        self.sock = ns
        self.lock = data_mutex
        self.users = users
        self.current_user = None

    def send_message(self, message):
        self.sock.send(pickle.dumps({"type": "message", "message": message}))

    def register(self, req):
        with self.lock:
            self.current_user = User(req.email, req.namesurname, req.password, req.balance)
            self.send_message(self.sock, "User created.")
    
    def close(self):
        self.send_message(self.sock, "Selametle yine bekleriz.")
        self.sock.close()

    def login(self, req):
        with self.lock:
            try:
                self.current_user = self.users[req["email"]]
            except:
                self.send_message("User cannot be found.")
            if self.current_user.password != req["password"]
                self.send_message("Password is incorrect.")
            else:
                self.send_message("Successfully login.")

    def user_operations(self, req):
        user_methods = {
            "verify": None,
            "change_password": None,
            "listitems": None,
            "report": None,
            "sell_item": None,
        }
        user_methods[req["operation"]](req)

    def create_sell_item(self, req):
        with self.lock:
            item = SellItem(self.current_user, req["title"], 
                            req["itemtype"], req["description"], 
                            req["auction_type"], req["starting"],
                            req["minbid"],req["image"])

    def sell_item_operations(self, req):
        sell_item_methods = {
            "create_item": self.create_sell_item,
            "start_auction": None,
            "bid": None,
            "sell": None,
            "view": None,
            "history": None
        }
        sell_item_methods[req["operation"]](req)

    def run(self):
        while True:
            req = pickle.load(sock.recv(1000))

            if req["type"] == "register":
                self.register(req)
                print("Register succesful.")
            elif req["type"] == "close":
                self.close()
                print("Connection closed.")
                break
            elif req["type"] == "login":
                self.login(req)
                print("Login succesful.")
            elif req["type"] == "sell_item":
                self.sell_item_operations(req)
            elif req["type"] == "user":
                self.user_operations(req)

def server(port):
    data_mutex = Lock()
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('',port))
    s.listen(10)    # 1 is queue size for "not yet accept()'ed connections"
    users = {}
    items = {}
    try:
        #while True:
        for i in range(5):    # just limit # of accepts for Thread to exit
            ns, peer = s.accept()
            print(peer, "connected")
            
            t = Agent(ns,data_mutex,users)
            t.start()
            # now main thread ready to accept next connection
    finally:
        s.close()

if __name__ == "__main__":
    server = Thread(target=server, args=(20445,))
    server.start()
