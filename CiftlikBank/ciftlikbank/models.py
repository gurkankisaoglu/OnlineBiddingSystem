from django.db import models
from django.contrib.auth.models import User 

# Create your models here.
class Person(models.Model):
    namesurname = models.CharField(max_length=30)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null = True)
    balance = models.IntegerField()
    reserved_balance = models.IntegerField()
    expenses = models.IntegerField()
    income = models.IntegerField()

STATES = (
    ('onhold', 'ONHOLD'),
    ('active', 'ACTIVE'),
    ('sold', 'SOLD')
)

class SellItem(models.Model):
    owner = models.ForeignKey(Person, related_name='owner',on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    itemtype = models.CharField(max_length=30)
    description = models.CharField(max_length=30)
    auction_type = models.CharField(max_length=30)
    image= models.ImageField()
    state = models.CharField(max_length=6,choices=STATES, default='onhold')
    auction_started = models.BooleanField(default=False)
    current_bidder = models.ForeignKey(Person, related_name='current_bidder', on_delete=models.DO_NOTHING)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BidRecord(models.Model):
    bidder =  models.ForeignKey(Person, on_delete=models.CASCADE)
    item = models.ForeignKey(SellItem, on_delete=models.CASCADE)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class UserNotification(models.Model):
    user = models.ForeignKey(Person, on_delete=models.CASCADE)
    message = models.CharField(max_length=100)