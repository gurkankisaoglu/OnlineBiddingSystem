from threading import *
import json
import pickle
from User import User
from Sellitem import SellItem
from socket import *
import random


class Agent(Thread):
    def __init__(self, ns, data_mutex, users, items):
        Thread.__init__(self)
        self.sock = ns
        self.lock = data_mutex
        self.users = users
        self.items = items
        self.current_user = None

    def send_message(self, message):
        self.sock.send(pickle.dumps({"type": "message", "message": message}))
    
    def send_notify(self, message):
        self.sock.send(pickle.dumps({"type": "notify", "notification_message": message}))

    def send_object(self, obj):
        self.sock.send(pickle.dumps({"type": "object", "object": obj}))

    def register(self, req):
        with self.lock:
            self.current_user = User(req["email"], req["namesurname"], req["password"], req["balance"])
            self.send_message("User created.")
            self.users[self.current_user.email] = self.current_user
            with open("verification.json") as f:
                data = dict(json.load(f))
                self.send_message(data[req["email"]]["number"])
    
    def close(self):
        self.send_message("Selametle yine bekleriz.")
        print("closing connection")
        self.sock.close()

    def login(self, req):
        with self.lock:
            if req["email"] in self.users and req["password"] == self.users[req["email"]].password:
                self.send_message("Successfully login.")
                self.current_user = self.users[req["email"]]
            else:
                self.send_message("Login failed!")    

    def verify(self, req):
        with self.lock:
            try:
                User.verify(self.current_user.email, req["verification_number"])
                print("asdasd")
                self.send_message("OK")
            except Exception as e:
                self.send_message(e)

    def change_password(self, req):
        try:
            self.current_user.changepassword(req["new_password"], req["old_password"])
            self.send_message("OK")
        except ValueError as e:
            self.send_message(e)

    def list_items(self, req):
        with self.lock:
            ret = self.current_user.listitems(self.users[req["email"]], 
                                        req["item_type"], 
                                        req["state"])
            self.send_object(ret)

    def report(self, req):
        with self.lock:
            self.send_object(self.current_user.report())
            self.send_message("OK")

    def sell_item(self, req):
        with self.lock:
            try:
                self.current_user.sell_item(self.items[req["title"]])
                self.send_message("OK")
            except Exception as e:
                self.send_message(e)

    def user_operations(self, req):
        user_methods = {
            "verify": self.verify,
            "change_password": self.change_password,
            "listitems": self.list_items,
            "report": self.report,
            "sell_item": self.sell_item,
        }
        user_methods[req["operation"]](req)

    def create_sell_item(self, req):
        with self.lock:
            item = SellItem(self.current_user, req["title"], 
                            req["itemtype"], req["description"], 
                            req["auction_type"], req["starting"],
                            req["minbid"],req["image"])
            self.items[item.title] = item
            print("created")
            self.send_message("OK")

    def start_auction(self, req):
        try:
            self.items[req["title"]].startauction(self.current_user)
            self.send_message("OK")
        except Exception as e:
            self.send_message(e)

    def bid(self, req):
        with self.lock:
            try:
                self.items[req["title"]].bid(self.current_user, req["amount"])
                self.send_message("OK")
            except Exception as e:
                self.send_message(e)

    def sell(self, req):
        with self.lock:
            try:
                self.items[req["title"]].sell(self.current_user)
                self.send_message("OK")
            except Exception as e:
                self.send_message(e)

    def view(self, req):
        with self.lock:
            self.send_object(self.items[req["title"]].view())

    def history(self, req):
        with self.lock:
            self.send_object(self.items[req["title"]].history())

    def notify(self, message):
        self.send_notify(message)

    def watch(self, req):
        with self.lock:
            try:
                self.items[req["title"]].watch(self.current_user, self.notify)
                self.send_message("OK")
            except:
                self.send_message("Watch failed!")

    def sell_item_operations(self, req):
        sell_item_methods = {
            "create_item": self.create_sell_item,
            "start_auction": self.start_auction,
            "bid": self.bid,
            "sell": self.sell,
            "view": self.view,
            "history": self.history,
            "watch": self.watch
        }
        sell_item_methods[req["operation"]](req)

    def run(self):
        try:
            while True:
                req = pickle.loads(self.sock.recv(1000))
                print(req)
                if req["type"] == "register":
                    self.register(req)
                elif req["type"] == "close":
                    self.close()
                    break
                elif req["type"] == "login":
                    self.login(req)
                elif req["type"] == "sell_item":
                    self.sell_item_operations(req)
                elif req["type"] == "user":
                    self.user_operations(req)
        except KeyboardInterrupt:
            print("closing...")
            return

def server(port):
    data_mutex = Lock()
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('',port))
    s.listen(10)    # 1 is queue size for "not yet accept()'ed connections"
    print("server ready..! port {}".format(port))
    users = {}
    items = {}
    try:
        #while True:
        for i in range(5):    # just limit # of accepts for Thread to exit
            ns, peer = s.accept()
            print(peer, "connected")
            
            t = Agent(ns,data_mutex,users,items,)
            t.start()
            # now main thread ready to accept next connection
    except:
        s.close()
    finally:
        s.close()

if __name__ == "__main__":
    port = random.randint(1024, 49151)
    with open("port.txt", "w") as f:
        f.write(str(port))
    server(port)

