from User import User
from Sellitem import SellItem

owner = User("email", "asd", "pass")
token = input("enter token\n")
User.verify("email", token)

buyer = User("buyer", "asd", "ppp")
token = input("enter token\n")
User.verify("buyer", token)

buyer2 = User("buyer2", "asd2", "ppp2")
token = input("enter token\n")
User.verify("buyer2", token)


buyer.addBalance(1000)
buyer2.addBalance(5000)

item = SellItem(owner,"title", "typ", "desc", "inc", 10, 2.0)

try:
    item.bid(buyer,5)
except Exception as e:
    print(e)

item.startauction(40)

try:
    item.bid(buyer,11)
except Exception as e:
    print(e)

try:
    item.bid(buyer2,10)
except Exception as e:
    print(e)

try:
    item.bid(buyer2,50)
except Exception as e:
    print(e)

print(buyer.reserved_balance)
print(buyer.balance)

print(buyer2.reserved_balance)
print(buyer2.balance)

item.sell()

print(buyer.reserved_balance)
print(buyer.balance)

print(buyer2.reserved_balance)
print(buyer2.balance)

print(buyer2.items[0].title)
print(owner.items)
