"""
 Decrement Auction test for automatic stop functionality 
"""


from User import User
from Sellitem import SellItem
import time

print("\nItem owner is created and verified")
item_owner = User("owner_mail@mail.com", "name surname", "password123")
User.verify(item_owner.email,item_owner.verification_number)
print("\nBuyer1 created and verified")
buyer1 = User("buyer1_mail@mail.com", "bedirhan uguz", "password123")
User.verify(buyer1.email,buyer1.verification_number)
buyer1.addBalance(10 * 1000)

item = SellItem(item_owner, "Tofas Sahin", "Car", "Doktordan az kullanilmis.",\
    ("decrement",1,500,5000),6000,1)
print("\nAdding item to item_owner, with auction type={} starting={}".format(item.auction_type,item.current_value))

print("\nbuyer1 watches to item with item.watch()")
item.watch(buyer1, buyer1.notification)

print("\nAuction started and we will wait 2 min to see price drop and stop auto.")
item.startauction(owner=item_owner)
time.sleep(121)

print("\n\nAuction stoped \n\n")


print("\nBuyer1 tries to bid 1000!\
 It should deny since auction is not started")
try:
    item.bid(buyer1, 1000)
    print("\nBid success!")
    print("\nitem view: ", item.view())
except Exception as e:
    print("\nFailed with message: ",e)

print("\nsee item view and history: \n")
print("item_view: ", item.view())
print("\nitem_history:", item.history())
print("\n\n Test Finished")