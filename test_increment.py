from User import User
from Sellitem import SellItem

owner = User("owner@mail.com","owner surname", "pass1234",500)
User.verify("owner@mail.com", owner.verification_number)

user2 = User("user2@mail.com","user surname", "pass1234", 1000)
User.verify("user2@mail.com", user2.verification_number)

bidder = User("bidder@email.com", "bidder surname", "pass12346", 1500)
User.verify("bidder@email.com", bidder.verification_number)

bidder2 = User("bid@gmail.com", "name bidder surname", "assadqwsad", 10000)
User.verify("bid@gmail.com", bidder2.verification_number)

item = SellItem(owner, "item name", "itemtype", "descr", ("increment", 5, 1000), 50)

item.startauction(owner)

print("\nuser2 tries to bid 5")
try:
    item.bid(user2, 5)
except Exception as e:
    print(e)


print("\nuser2 tries to bid -5")
try:
    item.bid(user2, -5)
except Exception as e:
    print(e)

item.bid(bidder,750)

item.bid(bidder2, 1000)

print(user2.report())
print(bidder.report())
print(bidder2.report())

item2 = SellItem(owner, "item2 name", "itemtype", "descr", ("increment", 5, 1000), 50)

item2.startauction(owner)

item2.bid(user2, 500)

item2.bid(bidder2,750)

print("\nbidder bids 1500. stopbid is 1000")
item2.bid(bidder, 1500)

print(user2.report())
print(bidder.report())
print(bidder2.report())
