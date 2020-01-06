from django.contrib import admin
from ciftlikbank.models import Person, SellItem, BidRecord, UserNotification

class PersonAdmin(admin.ModelAdmin):
  list_display = ('namesurname','user','balance','reserved_balance','expenses')

class SellItemAdmin(admin.ModelAdmin):
  list_display = ("title", "owner", "itemtype", "auction_type", "state", "current_bidder", "current_value", "description", "auction_started_at", "created_at")

class BidRecordAdmin(admin.ModelAdmin):
  list_display = ("bidder", "item", "amount", "created_at")

class UserNotificationAdmin(admin.ModelAdmin):
  list_display = ("user", "notification_type", "item_id", "itemtype")

# Register your models here.
admin.site.register(Person, PersonAdmin)
admin.site.register(SellItem, SellItemAdmin)
admin.site.register(BidRecord, BidRecordAdmin)
admin.site.register(UserNotification, UserNotificationAdmin)