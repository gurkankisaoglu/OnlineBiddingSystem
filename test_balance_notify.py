from User import User
from Sellitem import SellItem

owner = User("owner@mail.com","owner surname", "pass1234",500)
User.verify("owner@mail.com", owner.verification_number)

owner2 = User("owner2@mail.com","user surname", "pass1234", 1000)
User.verify("owner2@mail.com", owner2.verification_number)

bidder = User("bidder@email.com", "bidder surname", "pass12346", 1500)
User.verify("bidder@email.com", bidder.verification_number)

bidder2 = User("bid@gmail.com", "name bidder surname", "assadqwsad", 10000)
User.verify("bid@gmail.com", bidder2.verification_number)


item = SellItem(owner, "item name", "itemtype", "descr", ("increment", 5, 1000), 50)


def notf(*args):
    print("bidder2 is notified with => "
        + args[0])

bidder2.watch("itemtype",notf)

item2 = SellItem(owner2, "item name 2", "itemtype", "descr", ("increment", 5, 1000), 50)

item.startauction(owner)

item2.startauction(owner2)

print(owner.report())
print(owner2.report())


print("Buyer balance is 1500. Bids 900 to item1 and 900 to item2")

try:
    item.bid(bidder,900)

    item2.bid(bidder,900)

except Exception as e:
    print(e)

print("\nbidder balance not changed because item not sold to bidder")
print(bidder.report())
print(owner.report())

item.sell(owner)

print("\nAfter owner call sell method bidder balance decreased")
print(bidder.report())
print(owner.report())

print("\n")
print(owner2.report())
print("owner2 release onsale item")
owner2.release_item(item2)
print(owner2.report())

