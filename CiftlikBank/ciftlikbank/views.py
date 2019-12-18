from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import  authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from ciftlikbank.models import Person, SellItem, BidRecord
from django.contrib.auth.models import User
from ciftlikbank.forms import SignUpForm, SellItemForm
import json
import datetime

def sign_in(request):
	if 'username' in request.POST and 'password' in request.POST:
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(request, username=username, password=password)
			if user is not None:
				login(request, user)   # this sets the session, 

	else:    
			return render(request,'login.html',{'form': AuthenticationForm})


def logout_view(request):
		logout(request)

@login_required
def index(request):
	owner = User.objects.get(id = request.user.id)
	user_items = SellItem.objects.filter(owner=owner)
	active_items = SellItem.objects.filter(state='active').exclude(owner=owner)
	sold_items = SellItem.objects.filter(state='sold')
	
	
	return render(request,'index.html',
		{
			"user_items": user_items,
			"active_items": active_items,
			"sold_items": sold_items
		}
	)

@login_required
def view_item(request,item_id):
	try:
		item = SellItem.objects.get(id=item_id)
	except ObjectDoesNotExist:
		return redirect("/")
	try:
		bids = BidRecord.objects.filter(item=item_id)
	except ObjectDoesNotExist:
		return redirect("/")
	
	return render(request, "item.html",{'item': item, 'bids': bids})

@login_required
def start_auction(request, item_id):
	item = SellItem.objects.get(id=item_id)
	if not item.auction_started:
		item.auction_started = True
		item.state = "active"
		item.auction_started_at = datetime.datetime.now()
		item.save()
	return redirect("/ciftlikbank/view/{}".format(item_id))

@login_required
def sell_item(request,item_id):
	item = SellItem.objects.get(id=item_id)
	
@login_required
def sell_item_create(request):
	message = "Here you can create SellItem"
	if request.method == 'POST':
		form = SellItemForm(request.POST, request.FILES)
		if form.is_valid():
			title = form.cleaned_data.get('title')
			itemtype = form.cleaned_data.get('itemtype')
			description =  form.cleaned_data.get('description')
			auction_type =  form.cleaned_data.get('auction_type')
			image =  form.cleaned_data.get('image')

			owner = User.objects.get(id = request.user.id)
			auction_type = auction_type.split(',')
			_auction_type = {}
			if auction_type[0] == 'increment':
				_auction_type["type"] = auction_type[0]
				_auction_type["mindelta"] = int(auction_type[1])
				_auction_type["instantsell"] = int(auction_type[2])

			elif auction_type[0] == 'decrement':
				_auction_type["type"] = auction_type[0]
				_auction_type["period"] = int(auction_type[1])
				_auction_type["delta"] = int(auction_type[2])
				_auction_type["stopbid"] = int(auction_type[3])

			elif auction_type[0] == 'instantincrement':
				_auction_type["type"] = auction_type[0]
				_auction_type["minbid"] = int(auction_type[1])
				_auction_type["autosell"] = int(auction_type[2])

			_auction_type = json.dumps(_auction_type)

			SellItem.objects.create(
				owner=owner, title=title, itemtype=itemtype,
				description=description, auction_type=_auction_type,
				image=image
			)
	
			message = "SellItem Created with title:{}".format(title)
	else:
		form = SellItemForm()
	return render(request, 'sell_item_form.html', {'form': form, 'message':message})

@login_required
def make_bid(request):
	return render(request,'bid_form.html')

def register(request):
	'''Show and process registration page
			 uid is required for admin users to register a specific student
	'''

	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password1')
			email =  form.cleaned_data.get('email')
			namesurname =  form.cleaned_data.get('namesurname')
			balance =  form.cleaned_data.get('balance')
			user = authenticate(username=username,email=email,password=password)
			person = Person.objects.create(user=user,namesurname=namesurname,balance=balance,
											reserved_balance=0,expenses=0,income=0)

			login(request, user)
			return redirect('home')
	else:
		form = SignUpForm()
	    
	return render(request, 'register.html', {'form': form, 'message': "message from view"})
