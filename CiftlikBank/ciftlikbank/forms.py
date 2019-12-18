from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from ciftlikbank.models import SellItem


class SignUpForm(UserCreationForm):
    namesurname = forms.CharField(max_length=30, required=True, help_text='Name and surname.')
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Inform a valid email address.')
    balance = forms.IntegerField(required=True, min_value=0, help_text="User Balance")
    class Meta:
        model = User
        fields = ('username', 'namesurname', 'email', 'password1', 'password2', 'balance',)



class SellItemForm(forms.Form):
    title = forms.CharField(max_length=30)
    itemtype = forms.CharField(max_length=30)
    description = forms.CharField(max_length=30)
    auction_type = forms.CharField(max_length=30,help_text='example: increment,mindelta,instantsell')
    image = forms.ImageField()
    