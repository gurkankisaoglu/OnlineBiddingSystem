from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import  authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.core.mail import send_mail
from ciftlikbank.models import Person, SellItem, BidRecord
from django.contrib.auth.models import User
from ciftlikbank.forms import SignUpForm, SellItemForm
from background_task import background
from background_task.tasks import Task
import json
import datetime
import secrets

def sign_in(request):
	if 'username' in request.POST and 'password' in request.POST:
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(request, username=username, password=password)
			if user is not None:
				login(request, user)   # this sets the session, 
				return redirect("/")
	else:    
			return render(request,'login.html',{'form': AuthenticationForm})


def logout_view(request):
		logout(request)

@login_required
def index(request):

	owner = User.objects.get(id = request.user.id)
	user_items = SellItem.objects.filter(owner=owner)
	active_items = SellItem.objects.filter(state='active').exclude(owner=owner)
	sold_items = SellItem.objects.filter(state='sold').exclude(owner=owner)
	person = Person.objects.get(user_id = request.user.id)
	
	all_users = User.objects.all()

	return render(request,'index.html',
		{
			"user_items": user_items,
			"active_items": active_items,
			"sold_items": sold_items,
			"person": person,
			"all_users": all_users
		}
	)

@login_required
def view_user(request,uid, message=""):
	try:
		view_person = Person.objects.get(user_id = uid)
		max_withdraw = view_person.balance - view_person.reserved_balance
		own_items = SellItem.objects.filter(owner_id = uid )
		bought_items = SellItem.objects.filter(owner_id = uid,old_owner_id__isnull = False)
		sold_items = SellItem.objects.filter(old_owner_id = uid)
	except:
		return redirect('/ciftlikbank')

	return render(request, "user.html",{
								'view_person': view_person, 'own_items': own_items,
								'bought_items': bought_items, 'sold_items': sold_items,	
								"person": Person.objects.get(user_id = request.user.id),
								"max_withdraw": max_withdraw,
								"message": message
								})

@login_required
def addbalance(request,uid):
	with transaction.atomic():
		person = Person.objects.select_for_update().get(user_id=request.user.id)
		person.balance += int(request.POST.get('addbalance',0))
		person.save()
		return view_user(request,uid)

@login_required
def withdraw(request,uid):
	with transaction.atomic():
		person = Person.objects.select_for_update().get(user_id=request.user.id)
		person.balance -= int(request.POST.get('withdraw',0))
		person.save()
		return view_user(request,uid)

@login_required
def view_item(request,item_id,message=""):
	try:
		item = SellItem.objects.get(id=item_id)
	except:
		return redirect("/ciftlikbank")
	try:
		bids = BidRecord.objects.filter(item=item_id)
	except :
		return redirect("/ciftlikbank")
	
	return render(request, "item.html",{
								'item': item, 'bids': bids,	
								"person": Person.objects.get(user_id = request.user.id),
								"message": message
								})

@login_required
def start_auction(request, item_id):
	item = SellItem.objects.get(id=item_id)
	if not item.owner_id == request.user.id:
		return view_item(request,item_id)
	if item.state == "onhold":
		item.auction_started = True
		item.state = "active"
		auction_type = json.loads(item.auction_type)
		if auction_type["type"] == "decrement":
			t = 5
			decr_count = (auction_type["starting"]-auction_type["stop"])//auction_type["delta"]+1
			dt = datetime.datetime.now() + datetime.timedelta(seconds=decr_count*t)
			decrement_price(item_id, schedule=t, repeat=t, repeat_until=dt)
		item.auction_started_at = datetime.datetime.now()
		item.save()
	return view_item(request,item_id)

@background
def decrement_price(item_id):
	print("called with item_id: ", item_id)
	with transaction.atomic():
		item = SellItem.objects.select_for_update().get(id=item_id)
		auction_type = json.loads(item.auction_type)
		if item.state == 'active':
			item.current_value -= auction_type["delta"]
		if item.current_value <= auction_type["stop"]:
			task = Task.objects.filter(task_params='[["%s"], {}]' % item_id)
			task.delete()
			item.old_owner = item.owner
			item.state = "sold"
			item.auction_ended_at = datetime.datetime.now()
		item.save()

@login_required
def bid_item(request, item_id):
	with transaction.atomic():
		if request.method == 'POST':
			try:
				item = SellItem.objects.select_for_update().get(id=item_id)
				person = Person.objects.select_for_update().get(user_id=request.user.id)
				owner = Person.objects.select_for_update().get(user_id=item.owner)
				if item.current_bidder:
					current_bidder = Person.objects.select_for_update().get(user_id=item.current_bidder.id)
			except:
				return redirect('/ciftlikbank')
			if item.state != "active":
				return view_item(request, item_id)

			amount = int(request.POST.get("bid_value", 0))
			auction_type = json.loads(item.auction_type)
			if auction_type["type"] == "increment":
				#Set remining balance
				if item.current_bidder == request.user:
					remaining_balance = person.balance - person.reserved_balance + item.current_value
				else:
					remaining_balance = person.balance - person.reserved_balance
				#make bid operations
				if amount - item.current_value < auction_type["mindelta"] or amount > remaining_balance:
					return view_item(request, item_id, message="Wrong amount!")
				elif amount > auction_type["instantsell"]:
					#user update
					if item.current_bidder == person.user:
						person.balance -= amount
						person.expenses += amount
						person.reserved_balance -= item.current_value
						person.save()
					elif current_bidder:
						current_bidder.reserved_balance -= item.current_value
						current_bidder.save()
					#item update
					owner.balance += amount
					owner.income += amount
					owner.save()
					item.state = "sold"
					item.auction_ended_at = datetime.datetime.now()
					item.old_owner = owner.user
					item.owner = request.user
					item.current_bidder = request.user
					item.current_value = amount
					item.save()
					BidRecord.objects.create(bidder=request.user, bidder_name=request.user.username, 
											item=item, amount=amount)
				else:
					#user update
					if item.current_bidder == request.user:
						person.reserved_balance -= item.current_value
					elif item.current_bidder:
						current_bidder.reserved_balance -= item.current_value
						current_bidder.save()
					person.reserved_balance += amount
					person.save()
					#item update
					item.current_value = amount
					item.current_bidder = request.user
					item.save()
					BidRecord.objects.create(bidder=request.user, 
											bidder_name=request.user.username, 
											item=item, amount=amount)
			elif auction_type["type"] == "instantincrement":
				if not (amount > auction_type["minbid"] and amount <= person.balance - person.reserved_balance):
					return view_item(request, item_id, message="Wrong amount!")
				if item.current_bidder == request.user:
					item.current_value += amount
					item.save()
					person.balance -= amount
					person.expenses += amount
					person.save()
				else:
					bids = item.bidrecord_set.filter(bidder=request.user)
					total_bid = amount
					for bid in bids:
						total_bid += bid.amount
					
					current_bids = item.bidrecord_set.filter(bidder=item.current_bidder)
					max_bidders = 0
					for b in current_bids:
						max_bidders += b.amount

					if total_bid >= max_bidders:
						if amount + item.current_value >= auction_type["autosell"]:
							owner.balance += item.current_value + amount
							owner.income += item.current_value + amount
							owner.save()
							item.old_owner = owner
							item.owner = request.user
							item.state = "sold"
							item.auction_ended_at = datetime.datetime.now()
						item.current_value += amount
						item.current_bidder = request.user
						item.save()
						person.balance -= amount
						person.expenses += amount
						person.save()
					else:
						if amount + item.current_value >= auction_type["autosell"]:
							owner.balance += item.current_value + amount
							owner.income += item.current_value + amount
							owner.save()
							item.old_owner = owner
							item.owner = item.current_bidder
							item.state = "sold"
							item.auction_ended_at = datetime.datetime.now()
						item.current_value += amount
						item.save()
						person.balance -= amount
						person.expenses += amount
						person.save()
						
				BidRecord.objects.create(bidder=request.user, 
										bidder_name=request.user.username, 
										item=item, amount=amount)
			elif auction_type["type"] == "decrement":
				if amount >= item.current_value:
					item.current_bidder = request.user
					item.current_value = amount
					item.state = 'sold'
					item.auction_ended_at = datetime.datetime.now()
					item.old_owner = owner.user
					item.owner = request.user
					item.save()

					owner.balance += amount
					owner.income += amount
					owner.save()

					person.balance -= amount
					person.expenses += amount
					person.save()

			return view_item(request, item_id)

@login_required
def sell_item(request,item_id):
	with transaction.atomic():
		task = Task.objects.filter(task_params='[["%s"], {}]' % item_id)
		if task:
			task.delete()
		try:
			item = SellItem.objects.get(id=item_id)
			if item.current_bidder:
				person = Person.objects.get(user=item.current_bidder)
			else:
				person = None
		except:
			return redirect('/ciftlikbank')
		if not item.owner_id == request.user.id:
			return view_item(request,item_id)
		if not item.state == 'active':
			return view_item(request,item_id)
		
		item.old_owner = item.owner
		if person:
			if json.loads(item.auction_type)["type"] == "increment":
				person.balance -= item.current_value
				person.reserved_balance -= item.current_value
				person.save()
			owner = Person.objects.get(user=item.owner)
			owner.balance += item.current_value
			owner.save()
			item.owner = item.current_bidder
		item.state = 'sold'
		item.auction_ended_at = datetime.datetime.now()
		item.save()
	return view_item(request,item_id)

@login_required
def delete_item(request,item_id):
	item = SellItem.objects.get(id=item_id)
	if not item.owner_id == request.user.id:
		return view_item(request,item_id)
	if item.state == 'active':
		return view_item(request,item_id,"ACTIVE ITEMS CAN NOT BE DELETED")
	
	item.delete()
	return redirect('/ciftlikbank')

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
				_auction_type["stop"] = int(auction_type[3])
				_auction_type["starting"] = int(auction_type[4])
				starting = int(auction_type[4])

			elif auction_type[0] == 'instantincrement':
				_auction_type["type"] = auction_type[0]
				_auction_type["minbid"] = int(auction_type[1])
				_auction_type["autosell"] = int(auction_type[2])

			_auction_type = json.dumps(_auction_type)
			
			if auction_type[0] == "decrement":
				SellItem.objects.create(
					owner=owner, title=title, itemtype=itemtype,
					description=description, auction_type=_auction_type,
					image=image, current_value=starting
				)
			else:
				SellItem.objects.create(
					owner=owner, title=title, itemtype=itemtype,
					description=description, auction_type=_auction_type,
					image=image
				)
	
			message = "SellItem Created with title:{}".format(title)
	else:
		form = SellItemForm()
	return render(request, 'sell_item_form.html', {'form': form, 'message':message, "person": Person.objects.get(user_id = request.user.id)})



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
			user.is_active = False
			user.save()
			person = Person.objects.create(user=user,namesurname=namesurname,balance=balance,
											reserved_balance=0,expenses=0,income=0)
			person.verification_number = secrets.token_urlsafe(32)
			send_mail(
				'Ciftlik Bank Verification',
				'Your Mail: {}\nVerification number: {}\n'.format(email,person.verification_number),
				'mehmetaydin@ciftlikbank.com',
				[email,]
			)
			print("###############")
			print("user email => ", email)
			print("verification number => " ,person.verification_number)
			print("###############")
			person.save()
			login(request, user)
			return redirect('home')
	else:
		form = SignUpForm()
	    
	return render(request, 'register.html', {'form': form, 'message': "Ciftlik Bank'a kaydol!"})

def verify(request):
	if request.method == "POST":
		email = request.POST.get("email")
		verf = request.POST.get("verification")
		user = User.objects.get(email=email)
		person = Person.objects.get(user=user)
		if person.verification_number == verf:
			user.is_active = True
			user.save()
		return redirect('/accounts/logout?next=/ciftlikbank')
	else:
		return render(request, 'verify.html')