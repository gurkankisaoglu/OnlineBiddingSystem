import time
import datetime
import utilities

class SellItem:
    """
     SellItem class docs
    """
    def __init__(self, owner, title, itemtype, description, bidtype, 
                starting, minbid = 1.0, image = None ):
        
        self.owner = owner
        self.owner.add_item(self)
        self.title = title
        self.itemtype = itemtype
        self.description = description
        self.bidtye = bidtype
        self.starting = starting
        self.minbid = minbid
        self.image = image

        self.auction_started = False
        self.bid_records = []
        self.creation_time = time.time()
        self.current_value = 0
        self.current_bidder = None
        self.auction_start_timestamp = None
        self.auction_end_timestamp = None
        
        self.stopbid = None

    def startauction(self, stopbid = None):
        if self.auction_started:
            raise Exception("Auction is already started at {}".format(utilities.dateformatter(self.auction_start_timestamp)))
        if stopbid:
            self.stopbid = stopbid

        self.auction_started = True
        self.auction_start_timestamp = time.time()
    
    def bid(self, user, amount):
        if not self.auction_started:
            raise Exception("Auction is not started")
        if(amount < self.minbid):
            raise Exception(" Bid amount is lower than minimum bid amount({})".format(self.minbid))
        if(amount < self.current_value):
            raise Exception(" Bid amount is lower than current value({}).".format(self.current_value))
        if(user.reserve_amount(amount)):
            if self.current_bidder:
                self.current_bidder.release_amount(self.current_value)
            self.current_value = amount
            self.current_bidder = user
            self.bid_records.append({"bidder": user, "amount": amount,"timestamp": time.time()})

            if self.stopbid and  amount >= self.stopbid:
                print("Satiyorum... Sattim!")
                self.auction_started = False
                self.current_bidder.checkout(amount,self,self.owner)
                self.owner = self.current_bidder
                
        else:
            raise Exception(" User does not have this much unreserved amount.")
            
    def sell(self):
        if self.auction_started:
            # OWNER SHOULD BE CHECKED, only owner can call sell()
            self.auction_started = False
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
        watchmethod(user)

    def history(self):
        return {
            "creation":  utilities.dateformatter(self.creation_time),
            "auction_start": utilities.dateformatter(self.auction_start_timestamp),
            "bids": self.bid_records
        }