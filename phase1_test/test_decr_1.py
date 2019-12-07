"""

Test for Decrement Auction
Several methods are tested also
Please follow the console outputs.

"""
from User import User
from Sellitem import SellItem
import time

print("/ Item owner is created and not verified")
item_owner = User("owner_mail@mail.com", "name surname", "password123")

print("\nTrying to changepassword without verify it should raise Not verified exception")
try:
    item_owner.changepassword("12121212","adasdas")
except Exception as e:
    print(e)
print("\nNow verify user\n")

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
print("buyer1 report:",buyer1.report())
print("buyer2 report:",buyer2.report())

item = SellItem(item_owner, "Tofas Sahin", "Car", "Doktordan az kullanilmis.",\
    ("decrement",1,500,3350),6000,1)
print("\nAdding item to item_owner, with auction type={} starting={}".format(item.auction_type,item.current_value))
print("\nUser item list: ", item_owner.listitems(item_owner,"Car"))
print("\nItem view: ", item.view())

print("\nbuyer1 and buyer2 watches to item with item.watch()")
item.watch(buyer1, buyer1.notification)
item.watch(buyer2, buyer2.notification)

print("\n Item owner tries to sell but auction is not started yet!")
try:
    item.sell(item_owner)
except Exception as e:
    print("\nFailed with message: ",e)

print("\nBuyer1 tries to bid 1000!\
 It should deny since auction is not started")
try:
    item.bid(buyer1, 1000)
    print("\nBid success!")
    print("\nitem view: ", item.view())
except Exception as e:
    print("\nFailed with message: ",e)

print("\nOwner starts auction")
try:
    item.startauction(owner=item_owner)
except Exception as e:
    print("\nFailed with message: ",e)

print("\nAuction started and we will wait 1 min to see price drop notification")
time.sleep(61)
print("\nYou should see the price changing -500")

print("\nBuyer1 tries to bid 1k but current is bigger than 1k bid must be denied")
try:
    item.bid(buyer1,1000)
except Exception as e:
    print("\nFailed with message: ",e)

print("\nBuyer2 tries to bid 5.6k. Item must be sold to Buyer2")
try:
    item.bid(buyer2,5600)
except Exception as e:
    print("\nFailed with message: ",e)
print("\n\nItem sold see Item view and history, Buyer1 and Buyer2 Report\n\n")
print("item_view: ", item.view())
print("\nitem_history:", item.history())
print("\nitem_owner_report: ",item_owner.report())
print("\nbuyer1_report: ",buyer1.report())
print("\nbuyer2_report: ",buyer2.report())
print("\n\n\n Test Finished!")
