import time
import datetime
import utilities
import threading as th
from User import User

from utilities import NotificationModule

class SellItem:
    """
     SellItem class docs
    """
    def __init__(self, owner, title, itemtype, description, bidtype, 
                starting, minbid = 1.0, image = None ):
        
        self.lock = th.Lock()

        self.owner = owner
        self.owner.add_item(self)
        self.title = title
        self.itemtype = itemtype
        self.description = description
        self.bidtype = bidtype
        self.minbid = minbid
        self.image = image
        self.auction_started = False
        self.bid_records = []
        self.creation_time = time.time()
        self.current_value = starting
        self.current_bidder = None
        self.auction_start_timestamp = None
        self.auction_end_timestamp = None
        self.obs = NotificationModule()
        
        self.bid_operator = 1 if self.bidtype == "increment" else -1

        self.obs.notify(self.itemtype, "Object Created")
        # {"itemtype": [callback1,calback2,..]}
        self.callbacks = {}

        self.stopbid = None

    def startauction(self, stopbid = None):
        if not (type(stopbid) is float or type(stopbid) is int):
            raise ValueError("amount is invalid")
        if self.auction_started:
            raise Exception("Auction is already started at {}".format(utilities.dateformatter(self.auction_start_timestamp)))
        if stopbid:
            self.stopbid = stopbid

        self.auction_started = True
        self.auction_start_timestamp = time.time()
        self.notify_user()
        self.obs.notify(self.itemtype,"Auction Started!")
    
    def bid(self, user, amount):
        if not (type(amount) is float or type(amount) is int):
            raise ValueError("amount is invalid")
        if not type(user) is User:
            raise ValueError("invalid user")
        with self.lock:
            if not self.auction_started:
                raise Exception("Auction is not started")
            if amount <= 0:
                raise ValueError("Bid cannot be <= zero!")
            if(self.bidtype=="increment" and amount <  self.minbid):
                raise ValueError(" Bid amount is lower than minimum bid amount({})".format(self.minbid))
            if(self.bid_operator * amount < self.bid_operator * self.current_value):
                raise ValueError(" Bid amount is lower than current value({}).".format(self.current_value))
            if(self.bid_operator * (amount-self.current_value) < self.bid_operator * self.minbid):
                raise ValueError(" Bid amount is lower than minimum bid amount({})".format(self.minbid))
            if(user.reserve_amount(amount)):
                if self.current_bidder:
                    self.current_bidder.release_amount(self.current_value)
                self.current_value = amount
                self.current_bidder = user
                self.bid_records.append({"bidder": user, "amount": amount,"timestamp": time.time()})

                if self.stopbid and  self.bid_operator * amount >= self.bid_operator * self.stopbid:
                    print("Satiyorum... Sattim!")
                    self.auction_started = False
                    self.current_bidder.checkout(amount,self,self.owner)
                    self.owner = self.current_bidder
                    
            else:
                raise Exception(" User does not have this much unreserved amount.")

            self.notify_user()
            
    def sell(self):
        with self.lock :
            if self.auction_started:
                # OWNER SHOULD BE CHECKED, only owner can call sell()
                self.auction_started = False
                self.notify_user()
                if self.current_value != 0 and self.current_bidder:
                    self.current_bidder.checkout(self.current_value,self, self.owner)
                    self.owner = self.current_bidder
        
    def view(self):
        return {
            "title": self.title,
            "description": self.description,
            "auction_start": utilities.dateformatter(self.auction_start_timestamp),
            "bids": self.bid_records,
            "current_value": self.current_value,
            "current_bidder": self.current_bidder,
            "owner": self.owner
        }

    def watch(self, user, watchmethod):
        if not type(user) is User:
            raise ValueError("invalid user")
        with self.lock :
            if user in self.callbacks:
                raise Exception("User is already add watch_list")
            self.callbacks[user] = watchmethod

    def history(self):
        return {
            "creation":  utilities.dateformatter(self.creation_time),
            "auction_start": utilities.dateformatter(self.auction_start_timestamp),
            "bids": self.bid_records
        }

    def notify_user(self,descr=""):
        for user in self.callbacks:
            self.callbacks[user]("Item state changed")
