from django.db import models
from django.contrib.auth.models import User as Us

# Create your models here.
class User(models.Model):
    namesurname = models.CharField(max_length=30)
    user = models.OneToOneField(Us, on_delete=models.CASCADE, null = True)
    balance = models.IntegerField()
    reserved_balance = models.IntegerField()
    expenses = models.IntegerField()
    income = models.IntegerField()
