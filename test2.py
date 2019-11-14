from User import User
from Sellitem import SellItem

item_owner = User("owner_mail@mail.com", "name surname", "password123")
token = input("enter token: ")
User.verify("owner_mail@mail.com",token)

buyer1 = User("buyer1_mail@mail.com", "name surname", "password123")
token = input("enter token: ")
User.verify("buyer1_mail@mail.com", token)

buyer2 = User("buyer2_mail@mail.com", "name surname", "password123")
token = input("enter token: ")
User.verify("buyer2_mail@mail.com", token)

buyer1.addBalance(10 * 1000)
buyer2.addBalance(7 * 1000)

print("Adding item to item_owner")
item = SellItem(item_owner, "Tofas Sahin", "Car", "Doktordan az kullanilmis.", "increment",6880,500)
#TODO: list items wrong!!!
#print("User item list: ", item_owner.listitems(item_owner))
print("Item view: ", item.view())

print("buyer1 and buyer2 watches to item with item.watch()")
item.watch(buyer1, buyer1.notification)
item.watch(buyer2, buyer2.notification)

print("Buyer1 tries to bid 1000!\
 It should deny since auction is not started")
try:
    item.bid(buyer1, 1000)
    print("Bid success!")
    print("item view: ", item.view())
except Exception as e:
    print("Failed with message: ",e)

