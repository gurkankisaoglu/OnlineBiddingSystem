from django.db import models
from django.contrib.auth.models import User 

# Create your models here.
class Person(models.Model):
    namesurname = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null = True)
    balance = models.IntegerField()
    reserved_balance = models.IntegerField()
    expenses = models.IntegerField()
    income = models.IntegerField()
    verification_number = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.namesurname


    def table_user(self):
        return {
            "id": self.user.id,
            "1": self.balance,
            "2": self.reserved_balance,
            "3": self.expenses,
            "4": self.income
        }



STATES = (
    ('onhold', 'ONHOLD'),
    ('active', 'ACTIVE'),
    ('sold', 'SOLD')
)

class SellItem(models.Model):
    owner = models.ForeignKey(User, related_name='owner',on_delete=models.CASCADE)
    old_owner = models.ForeignKey(User, related_name='old_owner',on_delete=models.DO_NOTHING,null=True)
    title = models.CharField(max_length=255)
    itemtype = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    auction_type = models.CharField(max_length=255)
    image = models.ImageField(upload_to='', null=True, blank=True)
    state = models.CharField(max_length=6,choices=STATES, default='onhold')
    auction_started = models.BooleanField(default=False)
    current_bidder = models.ForeignKey(User, null=True, related_name='current_bidder', on_delete=models.DO_NOTHING)
    current_value = models.IntegerField(default=0)
    auction_started_at = models.DateTimeField(null=True)
    auction_ended_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def table_start_auction(self):
        # do not send image it will not change
        return {
            "id": self.id,
            "1": str(self.owner),
            #"9": str(self.old_owner),
            #"itemtype": self.itemtype,
            #"description": self.description,
            #"auction_type": self.auction_type,
            "4": self.state,
            "6": self.auction_started,
            "7": str(self.auction_started_at),
            #"8": str(self.auction_ended_at),
            #"10": str(self.current_bidder),
            #"11": self.current_value,
            #"item_created_at": str(self.created_at)
        }

    def table_sell_item(self):
        return {
            "id": self.id,
            "1": str(self.owner),
            "4": self.state,
            "6": self.auction_started,
            "8": str(self.auction_ended_at),
            "10": str(self.current_bidder),
            "11": self.current_value,
            "9": str(self.old_owner)
        }
    
    def table_add_bid(self):
        return{
            "id": self.id,
            "10": str(self.current_bidder),
            "11": self.current_value
        }

class BidRecord(models.Model):
    bidder =  models.ForeignKey(User, on_delete=models.CASCADE)
    bidder_name = models.CharField(max_length=255, null=True)
    item = models.ForeignKey(SellItem, on_delete=models.CASCADE)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

NOTIFICATION_TYPES = (
    ('item', 'ITEM'),
    ('user', 'USER')
)

class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=4, choices=NOTIFICATION_TYPES, null=True)
    item_id = models.IntegerField(null=True, blank=True)
    itemtype = models.CharField(max_length=255, null=True)