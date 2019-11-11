import random
import string
from enum import Enum
import secrets
import json

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
        self.verification_number = secrets.token_urlsafe(32)
        self.items = [{'itemid':1, 'itemtype': "test", 'state': ItemState.active}]
        print(self.verification_number)
        self.verified = False
        data = None
        with open("verification.json", "r") as f:
            data = json.load(f)
        with open("verification.json", "w") as f:
            data[self.email] = {"number": self.verification_number, "status": False}
            json.dump(data,f)
        f.close()

    def __getattribute__(self, attr):
        method = object.__getattribute__(self, attr)
        if not method:
            raise Exception("Method %s not implemented" % attr)
        if method is self.isVerified:
            return method
        if callable(method):
            if self.isVerified() == False:
                with open("verification.json") as f:
                    data = json.load(f)
                    if data[self.email]["status"]:
                        self.verified  = True
                    else :
                        raise Exception("Email is not verified!")

        return method
        
    def isVerified(self):
        return self.verified

    @staticmethod
    def verify(email, verification_number):
        data = None
        with open("verification.json", "r") as f:
            data = json.load(f)
            if data[email]["number"] == verification_number:
                data[email]["status"] = True
            else:
                raise Exception("Verification number is not valid!")
        with open("verification.json", "w") as f:
            json.dump(data,f)
            


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
        ret = []
        for item in self.items:
            if item["itemtype"] == itemtype and item["state"] == state:
                ret.append(item)
        return ret

    def getItems(self):
        return self.items

    @staticmethod
    def watch(itemtype, watchmethod):
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
        pass

    def reserve_amount(self, amount):
        if amount <= self.balance - self.reserved_balance:
            self.reserved_balance += amount
            return True
        else:
            return False