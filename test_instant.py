from User import User
from Sellitem import SellItem

owner = User("owner@mail.com","owner surname", "pass1234",500)
User.verify("owner@mail.com", owner.verification_number)

bidder = User("bidder@email.com", "bidder surname", "pass12346", 1500)
User.verify("bidder@email.com", bidder.verification_number)

bidder2 = User("bid@gmail.com", "name bidder surname", "assadqwsad", 10000)
User.verify("bid@gmail.com", bidder2.verification_number)

owner.watch("type", owner.notification)
bidder.watch("type", bidder.notification)
bidder2.watch("type", bidder2.notification)

item = SellItem(owner, "title", "type", "new product", 
        ("instantincrement", 100,1000),0)

item.startauction(owner)

item.bid(bidder, 150)

item.bid(bidder2, 100)

print(item.view())
try:
    item.bid(bidder2, 50)
except Exception as e:
    print(e)


print("\nowner tries to bid")
try:
    item.bid(owner, 300)
except Exception as e:
    print(e)

print(item.view())
print(bidder.report())
print(bidder2.report())

try:
    item.bid(bidder2, 750)
except Exception as e:
    print(e)

print("\nitem sold to bidder2")
print(item.view())
print(bidder.report())
print(bidder2.report())
