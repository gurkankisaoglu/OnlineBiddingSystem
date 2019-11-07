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
        
        self.item_sold = False
        self.final_value = 0
        self.buyer = None
        self.sell_timestamp = None

    def __getattribute__(self, attr):
        method = object.__getattribute__(self, attr)
        if not method:
            raise Exception("Method %s not implemented" % attr)
        if callable(method):
            if self.item_sold:
                raise Exception("Item was sold to {} at {}"
                    .format(self.buyer.namesurname,utilities.dateformatter(self.sell_timestamp)))

        return method

    def startauction(self, stopbid = None):
        if stopbid is None:
            self.auction_started = True
            self.auction_start_timestamp = time.time()

        else:
            if not self.current_bidder is None:
                self.auction_started = False
                self.current_bidder.checkout(self.current_value,self,self.owner)
                self.final_value = self.current_value
                self.item_sold = True
                self.buyer = self.current_bidder
                self.sell_timestamp = time.time()
                self.auction_end_timestamp = time.time()
            else:
                self.item_sold = True
                self.auction_end_timestamp = time.time()

    
    def bid(self, user, amount):
        if(amount < self.minbid):
            raise Exception(" Bid amount is lower than minimum bid amount({})".format(self.minbid))
        if(amount < self.current_value):
            raise Exception(" Bid amount is lower than current value({}).".format(self.current_value))
        if(user.reserve_amount(amount)):
            self.current_bidder.release(amount)
            self.current_value = amount
            self.current_bidder = user
            self.bid_records.append({"bidder": user, "amount": amount,"timestamp": time.time()})
        else:
            raise Exception(" User does not have this much unreserved amount.")
            

    def sell(self):
        # OWNER SHOULD BE CHECKED, only owner can call sell()
        self.current_bidder.checkout(self.current_value,self, self.owner)
        self.final_value = self.current_value
        self.item_sold = True
        self.buyer = self.current_bidder
        self.sell_timestamp = time.time()
        

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
        pass

    def history(self):
        return {
            "creation":  utilities.dateformatter(self.creation_time),
            "auction_start": utilities.dateformatter(self.auction_start_timestamp),
            "bids": self.bid_records,
            "final_value": self.final_value,
        }