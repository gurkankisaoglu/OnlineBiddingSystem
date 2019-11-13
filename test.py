from User import User
from Sellitem import SellItem

owner = User("user@email.com", "asd", "pass")
#token = input("enter token\n")
#User.verify("user@email.com", token)

buyer = User("buyer@email.com", "asd", "ppp")
#token = input("enter token\n")
#User.verify("buyer@email.com", token)

buyer2 = User("buyer2@email.com", "asd2", "ppp2")
#token = input("enter token\n")
#User.verify("buyer2@email.com", token)

User.watch("typ",buyer.notification)

buyer.addBalance(1000)
buyer2.addBalance(5000)

item = SellItem(owner,"title", "typ", "desc", "decrement", 1000, 2.0)
item.watch(buyer2,buyer2.notification)

try:
    item.bid(buyer,750)
except Exception as e:
    print(e)

item.startauction(10)

print(item.view())

try:
    item.bid(buyer,750)
except Exception as e:
    print(e)

print(item.view())

try:
    item.bid(buyer2,500)
except Exception as e:
    print(e)

print(item.view())

try:
    item.bid(buyer2,-5)
except Exception as e:
    print(e)

print(item.view())



