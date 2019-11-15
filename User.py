import random
import string
from enum import Enum
import secrets
import json
from utilities import NotificationModule
import re


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
    
    obs = NotificationModule()

    def __init__(self, email, namesurname, password):
        if not re.search("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)" , email):
            raise ValueError("Email is not valid")
        self.email = email
        if not re.search("[A-Za-z]{2,25}\s[A-Za-z]{2,25}$", namesurname):
            raise ValueError("Namesurname is invalid")
        self.namesurname = namesurname
        if not re.search("^[a-zA-Z0-9_.+-]{8,16}$", password):
            raise ValueError("Password is invalid")
        self.password = password
        self.balance = 0
        self.reserved_balance = 0
        self.expenses = 0
        self.income = 0
        self.verification_number = secrets.token_urlsafe(32)
        self.items = []


        print(self.verification_number)
        self.verified = False
        data = {}
        try:
            with open("verification.json", "r") as f:
                data = json.load(f)
        except:
            pass
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
        if not re.search("^[a-zA-Z0-9_.+-]{8,16}$", newpassword):
            raise ValueError("Password is invalid")
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
        if not isinstance(user,User):
            raise ValueError("invalid user")
        if user.items == []:
            print("There is no item in itemlist of {}".format(user.namesurname))
        ret = []
        for item in user.items:
            if (item.itemtype == itemtype or itemtype == None) and (item.state == state or state == 'all'):
                ret.append(item)
        return ret

    @_validation_decorator
    def notification(self,descr="user.notification"):
        print("Notification to {} with descr:{}".format(self.namesurname,descr))

    @staticmethod
    def watch(itemtype, watchmethod):
        User.obs.register(itemtype,watchmethod)
    
    @_validation_decorator
    def addBalance(self, amount):
        if not (type(amount) is float or type(amount) is int):
            raise ValueError("amount is invalid")
        self.balance += amount

        if amount > 0:
            self.income += amount

    @_validation_decorator
    def report(self):
        items_sold = [i for i in self.items if i.state == "sold"]
        items_onsale = [i for i in self.items if i.state == "active"]
        
        return {
            "name": self.namesurname,
            "email": self.email,
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
        if not (type(amount) is float or type(amount) is int):
            raise ValueError("amount is invalid")
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