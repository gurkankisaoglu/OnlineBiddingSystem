from socket import *
import pickle
import utilities
import threading
import json
import time

socket_lock = threading.Lock()
lock = threading.Lock()

sock = utilities.connect(lock)


"""

    REGISTER

"""

sock.send(pickle.dumps({"type":"register",
                        "email": "new@mail.com",
                        "namesurname":"ad soyad", 
                        "password": "aaasssddd", 
                        "balance": 123}))
                        

"""

    VERIFY

"""
time.sleep(0.1)
sock.send(pickle.dumps({"type":"user", "operation": "verify", 
                        "verification_number": utilities.verf("new@mail.com")}))

sock.send(pickle.dumps({"type":"close"}))

sock.close()

sock = utilities.connect(lock)

"""

    LOGIN

"""

sock.send(pickle.dumps({"type":"login",
                        "email": "new@mail.com",
                        "password": "aaasssddd"}))

sock2 = utilities.connect(lock)

sock2.send(pickle.dumps({"type":"register",
                        "email": "user@mail.com",
                        "namesurname":"user name", 
                        "password": "qweasdzxc", 
                        "balance": 10000}))

time.sleep(0.1)
sock2.send(pickle.dumps({"type":"user", "operation": "verify", 
                        "verification_number": utilities.verf("user@mail.com")}))

"""

    SELL ITEM

"""

print("create item")

sock.send(pickle.dumps({"type":"sell_item",
                        "operation": "create_item",
                        "title": "car",
                        "itemtype": "sahin",
                        "description": "araba",
                        "auction_type": ("increment", 5, 1000),
                        "starting": 100,
                        "minbid": 1,
                        "image": None}))

"""

    BID WITHOUT START AUCTION

"""
print("bid without start")

sock2.send(pickle.dumps({"type":"sell_item", "operation": "bid", 
                        "title": "car",
                        "amount": 500}))
"""

    START AUCTION BY ANOTHER USER

"""

print("start auction by another user")
sock2.send(pickle.dumps({"type":"sell_item",
                        "operation": "start_auction",
                        "title": "car"
                        }))

"""

    SELL ITEM WATCH

"""

print("second user subscribed sell item")
sock2.send(pickle.dumps({"type":"sell_item",
                        "operation": "watch",
                        "title": "car"
                        }))

"""

    START AUCTION

"""

print("start auction")
sock.send(pickle.dumps({"type":"sell_item",
                        "operation": "start_auction",
                        "title": "car"
                        }))

"""

    BID BY SECOND USER

"""
print("bid")

sock2.send(pickle.dumps({"type":"sell_item", "operation": "bid", 
                        "title": "car",
                        "amount": 500}))

"""

    SOLD

"""

print("sell")
sock.send(pickle.dumps({"type":"sell_item",
                        "operation": "sell",
                        "title": "car"
                        }))

sock.send(pickle.dumps({"type":"close"}))
sock2.send(pickle.dumps({"type":"close"}))

sock.close()
sock2.close()