import random
import string
from enum import Enum

class ItemType(Enum):
    TEST = 1
    DENEME = 2

class ItemState(Enum):
    all = 1
    onhold = 1
    active = 2
    sold = 3

class User:
    def __init__(self, email, namesurname, password):
        self.email = email
        self.namesurname = namesurname
        self.password = password
        self.balance = 0
        self.reserved_balance = 0
        self.expenses = 0
        self.income = 0
        self.items = [{'itemid':1, 'itemtype': ItemType.TEST, 'state': ItemState.active}]

    @staticmethod
    def verify(email, verification_number):
        
        pass

    def changepassword(self, newpassword, oldpassword=None):
        if oldpassword is None:
            self.password = "".join([random.choice(string.ascii_letters) for i in range(15)])
            print("temp password is {}".format(self.password))
        else:
            if self.password == oldpassword:
                self.password = newpassword
            else:
                print("password is wrong")

    def listitems(self, user, itemtype = None, state='all'):
        user_items = user.getItems()
        ret = []
        for item in user_items:
            if item["itemtype"] == itemtype and item["state"] == state:
                ret.append(item)
        else:
            
    def getItems():
        return self.items

    @staticmethod
    def watch(itemtype=None, watchmethod):
        pass

    def addbalance(amount):
        self.balane += amount
        if amout > 0:
            self.income += amount

    def report(self):
        items_sold = [i for i in self.items if self.items['state'] == ItemState.sold]
        items_onsale = [i for i in self.items if self.items['state'] == ItemState.active]
        
        return {
            "items_sold": items_sold,
            "on_sale": items_onsale,
            "all_expenses": self.expenses,
            "income": self.income
        }

    def release_amount(self, amount):
        self.reserved_balance -= amount
        return True

    def checkout(self, amount, item, owner):
        self.reserved_balance -= amount
        self.items.append(item)
        owner.release_item(item)
        return True

    def release_item(self, item):
        #release item

    def reserve_amount(self, amount):
        if amount <= self.balance - self.reserved_balance:
            self.reserved_balance += amount
            return True
        else:
            return False