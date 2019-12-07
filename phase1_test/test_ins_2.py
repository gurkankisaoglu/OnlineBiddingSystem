from User import User
from Sellitem import SellItem
import time

print("\nItem Owner created and verified")
item_owner = User("owner_mail@mail.com", "name surname", "password123")
User.verify("owner_mail@mail.com",item_owner.verification_number)

print("\nBuyer1 created and verified")
buyer1 = User("buyer1_mail@mail.com", "bedirhan uguz", "password123")
User.verify("buyer1_mail@mail.com", buyer1.verification_number)

print("\nBuyer2 created and verified")
buyer2 = User("buyer2_mail@mail.com", "ozhan suat", "password123")
User.verify("buyer2_mail@mail.com", buyer2.verification_number)

print("\nadding balance to buyer1(10k) and buyer2(7k)")
buyer1.addBalance(10 * 1000)
buyer2.addBalance(7 * 1000)

item = SellItem(item_owner, "Tofas Sahin", "Car", "Doktordan az kullanilmis.",\
    ("instantincrement",100,6000,),0,1)
print("\nAdding item to item_owner, with auction type={} starting={}".format(item.auction_type,item.current_value))
print("\nUser item list: ", item_owner.listitems(item_owner,"Car"))
print("\nItem view: ", item.view())

print("\nbuyer1 and buyer2 watches to item with item.watch()")
item.watch(buyer1, buyer1.notification)
item.watch(buyer2, buyer2.notification)

item.startauction(item_owner)

print("\nBuyer1 tries to bid 12k but he has 10k")
try:
    item.bid(buyer1,12000)
except Exception as e:
    print("\nFailed with message: ",e)
print("item_view: ", item.view())

print("\nBuyer1 tries to bid 1k")

try:
    item.bid(buyer1,1000)
except Exception as e:
    print("\nFailed with message: ",e)
print("\nitem_view: ", item.view())

print("\nBuyer2 tries to bid 2k")
try:
    item.bid(buyer2,2000)
except Exception as e:
    print("\nFailed with message: ",e)
print("\nitem_view: ", item.view())

print("\nBuyer1 tries to bid 1.5k more")
try:
    item.bid(buyer1,1500)
except Exception as e:
    print("\nFailed with message: ",e)
print("\nitem_view: ", item.view())

print("\n Item owner sells item")
try:
    item.sell(item_owner)
except Exception as e:
    print("\nFailed with message: ",e)

print("\n\nItem sold see Item view and history, Buyer1 and Buyer2 Report\n\n")
print("item_view: ", item.view())
print("\nitem_history:", item.history())
print("\nitem_owner_report: ",item_owner.report())
print("\nbuyer1_report: ",buyer1.report())
print("\nbuyer2_report: ",buyer2.report())
print("\n\n\n Test Finished!")
