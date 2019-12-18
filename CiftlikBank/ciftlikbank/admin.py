from django.contrib import admin
from ciftlikbank.models import Person, SellItem, BidRecord, UserNotification

class PersonAdmin(admin.ModelAdmin):
  list_display = ('namesurname','user','balance','reserved_balance','expenses')

class SellItemAdmin(admin.ModelAdmin):
  list_display = ("title", "owner", "itemtype", "auction_type", "state", "current_bidder", "current_value", "description", "auction_started_at", "created_at")

# Register your models here.
admin.site.register(Person, PersonAdmin)
admin.site.register(SellItem, SellItemAdmin)
admin.site.register(BidRecord)
admin.site.register(UserNotification)