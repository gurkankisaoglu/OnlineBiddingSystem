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
    def _validation_decorator(method):
        def validate(*args):
            if args[0].verified:
                return method(*args)
            else:
                with open("verification.json", "r") as f:
                    data = json.load(f)
                    args[0].verified = data[args[0].email]["status"]
                    if not args[0].verified:
                        raise Exception("Not verified")
                return method(*args)
        return validate

    def __init__(self, email, namesurname, password):
        self.email = email
        self.namesurname = namesurname
        self.password = password
        self.balance = 0
        self.reserved_balance = 0
        self.expenses = 0
        self.income = 0
        self.verification_number = secrets.token_urlsafe(32)
        self.items = []
        print(self.verification_number)
        self.verified = False
        data = None
        with open("verification.json", "r") as f:
            data = json.load(f)
        with open("verification.json", "w") as f:
            data[self.email] = {"number": self.verification_number, "status": False}
            json.dump(data,f)
        f.close()

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
            

    @_validation_decorator
    def changepassword(self, newpassword, oldpassword=None):
        if oldpassword is None:
            self.password = "".join([random.choice(string.ascii_letters) for i in range(15)])
            print("temp password is {}".format(self.password))
        else:
            if self.password == oldpassword:
                self.password = newpassword
            else:
                print("password is wrong")


    @_validation_decorator
    def listitems(self, user, itemtype = None, state='all'):
        ret = []
        for item in user.items:
            if item["itemtype"] == itemtype and item["state"] == state:
                ret.append(item)
        return ret

    @staticmethod
    def watch(itemtype, watchmethod):

        pass

    @_validation_decorator
    def addBalance(self, amount):
        self.balance += amount

        if amount > 0:
            self.income += amount

    @_validation_decorator
    def report(self):
        items_sold = [i for i in self.items if self.items['state'] == ItemState.sold]
        items_onsale = [i for i in self.items if self.items['state'] == ItemState.active]
        
        return {
            "items_sold": items_sold,
            "on_sale": items_onsale,
            "all_expenses": self.expenses,
            "income": self.income
        }

    @_validation_decorator
    def sell_item(self, item):
        if item in self.items:
            item.sell()
        else:
            raise Exception("Cannot be sold")

    @_validation_decorator
    def release_amount(self, amount):
        self.reserved_balance -= amount

    @_validation_decorator
    def checkout(self, amount, item, owner):
        self.reserved_balance -= amount
        self.balance -= amount
        owner.addBalance(amount)
        owner.release_item(item)
        self.add_item(item)

    @_validation_decorator
    def release_item(self, item):
        try:
            self.items.remove(item)
        except ValueError(e):
            raise Exception("item not found")
    
    @_validation_decorator
    def add_item(self, item):
        self.items.append(item)

    @_validation_decorator
    def reserve_amount(self, amount):
        if amount <= self.balance - self.reserved_balance:
            self.reserved_balance += amount
            return True
        else:
            return False