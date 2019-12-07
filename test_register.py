from socket import *
import pickle
import utilities
import threading
import json
import time

_time = 0.05

socket_lock = threading.Lock()
lock = threading.Lock()

sock = utilities.connect(lock)


"""

    REGISTER

"""

time.sleep(_time)
sock.send(pickle.dumps({"type":"register",
                        "email": "new@mail.com",
                        "namesurname":"ad soyad", 
                        "password": "aaasssddd", 
                        "balance": 123}))
                        

"""

    VERIFY

"""
time.sleep(_time)
sock.send(pickle.dumps({"type":"user", "operation": "verify", 
                        "verification_number": utilities.verf("new@mail.com")}))

time.sleep(_time)
sock.send(pickle.dumps({"type":"close"}))

sock.close()

sock = utilities.connect(lock)

"""

    LOGIN

"""

time.sleep(_time)
sock.send(pickle.dumps({"type":"login",
                        "email": "new@mail.com",
                        "password": "aaasssddd"}))

sock2 = utilities.connect(lock)

time.sleep(_time)
sock2.send(pickle.dumps({"type":"register",
                        "email": "user@mail.com",
                        "namesurname":"user name", 
                        "password": "qweasdzxc", 
                        "balance": 10000}))

time.sleep(_time)
sock2.send(pickle.dumps({"type":"user", "operation": "verify", 
                        "verification_number": utilities.verf("user@mail.com")}))

"""

    SELL ITEM

"""

print("create item")

time.sleep(_time)
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

time.sleep(_time)
sock2.send(pickle.dumps({"type":"sell_item", "operation": "bid", 
                        "title": "car",
                        "amount": 500}))
"""

    START AUCTION BY ANOTHER USER

"""

print("start auction by another user")
time.sleep(_time)
sock2.send(pickle.dumps({"type":"sell_item",
                        "operation": "start_auction",
                        "title": "car"
                        }))

"""

    SELL ITEM WATCH

"""

time.sleep(_time)
print("second user subscribed sell item")
sock2.send(pickle.dumps({"type":"sell_item",
                        "operation": "watch",
                        "title": "car"
                        }))

"""

    START AUCTION

"""

time.sleep(_time)
print("start auction")
sock.send(pickle.dumps({"type":"sell_item",
                        "operation": "start_auction",
                        "title": "car"
                        }))

"""

    BID BY SECOND USER

"""
print("bid")

time.sleep(_time)
sock2.send(pickle.dumps({"type":"sell_item", "operation": "bid", 
                        "title": "car",
                        "amount": 500}))

"""

    SOLD

"""

print("sell")
time.sleep(_time)
sock.send(pickle.dumps({"type":"sell_item",
                        "operation": "sell",
                        "title": "car"
                        }))

time.sleep(_time)
sock.send(pickle.dumps({"type":"close"}))
time.sleep(_time)
sock2.send(pickle.dumps({"type":"close"}))



sock.close()
sock2.close()