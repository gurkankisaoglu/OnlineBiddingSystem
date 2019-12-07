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

print("change password of owner user")
try:
    owner.changepassword("newpassword", "pass1234")
except Exception as e:
    print(e)


item = SellItem(owner, "item name", "itemtype", "descr", ("increment", 5, 1000), 50)



print("Item list of owner user")
print(user2.listitems(owner, "itemtype"))
print("Item list of other user")
print(user2.listitems(bidder, "itemtype"))


print("\nUser reports of owner and bidder at the start")
print(owner.report())
print(bidder.report())

item.startauction(owner)

print("\nUser reports of owner and bidder after auction started")
print(owner.report())
print(bidder.report())

item.bid(bidder,500)

item.sell(owner)

print("\nUser reports of owner and bidder after item sold")
print(owner.report())
print(bidder.report())