import time
import datetime
import utilities
import threading as th
from User import User
from utilities import NotificationModule
from apscheduler.schedulers.background import BackgroundScheduler

class SellItem:
    """
     SellItem class docs
    """
    def __init__(self, owner, title, itemtype, description, auction_type, 
                starting, minbid = 1.0, image = None ):
        
        self.lock = th.Lock()

        self.owner = owner
        self.owner.add_item(self)
        self.title = title
        self.itemtype = itemtype
        self.description = description
        self.auction_type = auction_type
        self.minbid = minbid
        self.image = image
        self.state = "onhold"
        self.auction_started = False
        self.bid_records = []
        self.creation_time = time.time()
        self.current_value = starting
        self.current_bidder = None
        self.auction_start_timestamp = None
        self.auction_end_timestamp = None
        self.obs = NotificationModule()
        
        #self.bid_operator = 1 if self.bidtype == "increment" else -1

        self.obs.notify(self.itemtype, "Object Created")
        # {"itemtype": [callback1,calback2,..]}
        self.callbacks = {}
        #self.stopbid = None

        if auction_type[0]== "decrement":
            self.scheduler = BackgroundScheduler()
            self.decrement_job = self.scheduler.add_job(
                self.__decrement_periodic,'interval', minutes = self.auction_type[1])
            self.scheduler.start(paused=True)
    def __decrement_periodic(self):
        with self.lock:
            self.current_value -= self.auction_type[2]
            self.notify_user("Price dropped! Current:{}".format(self.current_value))
            if self.current_value <= self.auction_type[3]:
                self.auction_started = False
                self.current_bidder = False
                self.scheduler.pause()
                self.notify_user("Price<=STOP stop:{}".format(self.auction_type[3]))
                self.state = "onhold"
    def startauction(self, owner = None):
        if owner != self.owner:
                raise Exception("User is not owner, can not sell")
        #if not (type(stopbid) is float or type(stopbid) is int):
        #    raise ValueError("amount is invalid")
        if self.auction_started:
            raise Exception("Auction is already started at {}".format(utilities.dateformatter(self.auction_start_timestamp)))
        #if stopbid:
        #    self.stopbid = stopbid
        self.state = "active"
        self.auction_started = True
        self.auction_start_timestamp = time.time()
        self.notify_user("Auction is started!")
        self.obs.notify(self.itemtype,"Auction Started!")
        if self.auction_type[0]== "decrement":
            self.scheduler.resume()
    
    def bid(self, user, amount):
        with self.lock:
            if not (type(amount) is float or type(amount) is int):
                raise ValueError("amount is invalid")
            if not type(user) is User:
                raise ValueError("invalid user")
            if not self.auction_started:
                raise Exception("Auction is not started")
            if amount <= 0:
                raise ValueError("Bid cannot be <= zero!")
            if amount <  self.minbid:
                raise ValueError(" Bid amount is lower than minimum bid amount({})".format(self.minbid))
            
            if self.auction_type[0]=="increment":
                if amount < self.current_value + self.auction_type[1]:
                    raise ValueError(" Bid amount is lower than current value+delta(current:{},delta:{})."\
                        .format(self.current_value,self.auction_type[1]))
                if(user.reserve_amount(amount)):
                    if self.current_bidder:
                        self.current_bidder.release_amount(self.current_value)
                    self.current_value = amount
                    self.current_bidder = user
                    self.bid_records.append({"bidder": user, "amount": amount,"timestamp": time.time()})
                    if self.auction_type[2] <= self.current_value:
                        print("Satiyorum... Sattim!")
                        self.bid_records.append({"bidder": user, "amount": amount,"timestamp": time.time()})
                        self.auction_started = False
                        self.auction_end_timestamp = time.time()
                        self.current_bidder.checkout(amount,self,self.owner)
                        self.owner = self.current_bidder
                        self.state = "sold"
                else:
                    raise Exception(" User does not have this much unreserved amount.")
            elif self.auction_type[0]=="decrement":
                if amount < self.current_value:
                    raise Exception("Auction type decrement. Value is lower than current({})".format(self.current_value))
                if(user.reserve_amount(amount)):
                    print("Satiyorum... Sattim!")
                    self.auction_started = False
                    self.auction_end_timestamp = time.time()
                    self.current_bidder = user
                    self.current_bidder.checkout(amount,self,self.owner)
                    self.bid_records.append({"bidder": user, "amount": amount,"timestamp": time.time()})
                    self.owner = self.current_bidder
                    self.scheduler.pause()
                    self.state = "sold"
                else:
                    raise Exception(" User does not have this much unreserved amount.") 

            else:
                print("INSTANT INCREMENT IS NOT IMPLEMENTED!")
                
            self.notify_user()
            
    def sell(self,owner = None):
        with self.lock :
            if owner != self.owner:
                raise Exception("User is not owner, can not sell")
            if not self.auction_started:
                raise Exception("Auction is not started yet!")
            # OWNER SHOULD BE CHECKED, only owner can call sell()
            self.auction_started = False
            self.state = "sold"
            self.notify_user()
            if self.current_value != 0 and self.current_bidder:
                self.current_bidder.checkout(self.current_value,self, self.owner)
                self.owner = self.current_bidder
        
    def view(self):
        return {
            "title": self.title,
            "description": self.description,
            "auction_start": utilities.dateformatter(self.auction_start_timestamp ) or "Auction is not started yet",
            "auction_end": utilities.dateformatter(self.auction_end_timestamp) or "Auction is not end",
            "bids": self.bid_records,
            "current_value": self.current_value,
            "current_bidder": self.current_bidder,
            "owner": self.owner
        }

    def watch(self, user, watchmethod):
        if not isinstance(user,User):
            raise ValueError("invalid user")
        with self.lock :
            if user in self.callbacks:
                raise Exception("User is already add watch_list")
            self.callbacks[user] = watchmethod

    def history(self):
        return {
            "creation":  utilities.dateformatter(self.creation_time),
            "auction_start": utilities.dateformatter(self.auction_start_timestamp),
            "bids": self.bid_records,
            "current_value": self.current_value
        }

    def notify_user(self,descr="Item state is changed"):
        for user in self.callbacks:
            self.callbacks[user](descr)
