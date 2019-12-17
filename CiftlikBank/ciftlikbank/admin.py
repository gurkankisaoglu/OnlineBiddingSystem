from django.contrib import admin
from ciftlikbank.models import Person, SellItem, BidRecord, UserNotification

class PersonAdmin(admin.ModelAdmin):
  list_display = ('namesurname','user','balance','reserved_balance','expenses')


# Register your models here.
admin.site.register(Person, PersonAdmin)
admin.site.register(SellItem)
admin.site.register(BidRecord)
admin.site.register(UserNotification)