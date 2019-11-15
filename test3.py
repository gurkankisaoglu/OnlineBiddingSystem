from User import User
from Sellitem import SellItem

owner = User("owner@mail.com","owner surname", "pass1234")
token = input("enter token: ")
User.verify("owner@mail.com", token)

user2 = User("user2@mail.com","user surname", "pass1234")
token = input("enter token: ")
User.verify("user2@mail.com", token)

bidder = User("bidder@email.com", "bidder surname", "pass12346")
token = input("enter token: ")
User.verify("bidder@email.com", token)

bidder2 = User("bid@gmail.com", "name bidder surname", "assadqwsad")
token = input("enter token: ")
User.verify("bid@gmail.com", token)

item = SellItem(owner, "item name", "itemtype", "descr", "increment", 50)

print("Item list of owner user")
print(user2.listitems(owner, "itemtype"))
print("Item list of other user")
print(user2.listitems(user2, "itemtype"))


print(owner.report())
print(user2.report())

item.startauction(1000)

print(owner.report())
print(user2.report())
