from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import  authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.core.mail import send_mail
from ciftlikbank.models import Person, SellItem, BidRecord, UserNotification
from django.contrib.auth.models import User
from ciftlikbank.forms import SignUpForm, SellItemForm
from background_task import background
from background_task.tasks import Task
import json
import datetime
import secrets
from django.http import JsonResponse
from ciftlikbank.consumers import SockConsumer


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
		own_items = SellItem.objects.filter(owner_id = uid,state='onhold')
		bought_items = SellItem.objects.filter(owner_id = uid,old_owner_id__isnull = False).exclude(old_owner_id=uid)
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
		SockConsumer.broadcast({
			"op": "user_change",
			"u": person.table_user()
		})
		
		return JsonResponse({"msg":"add balance"})

@login_required
def withdraw(request,uid):
	with transaction.atomic():
		person = Person.objects.select_for_update().get(user_id=request.user.id)
		person.balance -= int(request.POST.get('withdraw',0))
		person.save()
		SockConsumer.broadcast({
			"op": "user_change",
			"u": person.table_user()
		})
		return JsonResponse({"msg":"withdraw"})

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
			t = auction_type["period"]*60
			decr_count = (auction_type["starting"]-auction_type["stop"])//auction_type["delta"]+1
			dt = datetime.datetime.now() + datetime.timedelta(seconds=decr_count*t)
			decrement_price(item_id, schedule=t, repeat=t, repeat_until=dt)
		item.auction_started_at = datetime.datetime.now()
		item.save()

	SockConsumer.broadcast({
		"op": "item_view_change",
		"item": item.table_start_auction(),
		"action": "started"
	})
	notf_records = UserNotification.objects.filter(itemtype=item.itemtype)
	users = [obj.user.id for obj in notf_records]
	SockConsumer.send_notification(users, { 
		"op": "notification",
		"message": "Item created with {} type and auction started!".format(item.itemtype)
		})
	return JsonResponse({"msg": "start auction button is pressed!"})

@background
def decrement_price(item_id):
	with transaction.atomic():
		item = SellItem.objects.select_for_update().get(id=item_id)
		auction_type = json.loads(item.auction_type)
		if item.state == 'active':
			item.current_value -= auction_type["delta"]
		if item.current_value <= auction_type["stop"]:
			task = Task.objects.select_for_update().filter(task_params='[["%s"], {}]' % item_id)
			task.delete()
			item.old_owner = item.owner
			item.state = "sold"
			item.auction_ended_at = datetime.datetime.now()
			notf_records = UserNotification.objects.filter(item_id=item_id)
			users = [obj.user.id for obj in notf_records]
			SockConsumer.send_notification(users, { 
				"op": "notification",
				"message": "Auction of {} ended. There is no bid.".format(item.title)
			})
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
				else:
					current_bidder = None
			except:
				return redirect('/ciftlikbank')


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
					return JsonResponse({"status":"NOK","msg":"Wrong amount!"})
				elif amount >= auction_type["instantsell"]:
					#user update
					if item.current_bidder == person.user:
						person.balance -= amount
						person.expenses += amount
						person.reserved_balance -= item.current_value
					else:
						person.balance -= amount
						person.expenses += amount

					
					if current_bidder:
						current_bidder.reserved_balance -= item.current_value

					#item update
					owner.balance += amount
					owner.income += amount
					item.state = "sold"
					item.auction_ended_at = datetime.datetime.now()
					item.old_owner = owner.user
					item.owner = request.user
					item.current_bidder = request.user
					item.current_value = amount
					BidRecord.objects.create(bidder=request.user, bidder_name=request.user.username, 
											item=item, amount=amount)
					person.save()
					owner.save()
					if current_bidder:
						current_bidder.save()
					item.save()
				else:
					#user update
					if item.current_bidder == request.user:
						person.reserved_balance -= item.current_value
					elif item.current_bidder:
						current_bidder.reserved_balance -= item.current_value
					person.reserved_balance += amount
					#item update
					item.current_value = amount
					item.current_bidder = request.user
					BidRecord.objects.create(bidder=request.user, 
											bidder_name=request.user.username, 
											item=item, amount=amount)
					if current_bidder:
						current_bidder.save()
					item.save()
					person.save()
			elif auction_type["type"] == "instantincrement":
				if not (amount >= auction_type["minbid"] and amount <= person.balance - person.reserved_balance):
					return JsonResponse({"status":"NOK","msg":"Wrong amount!"})
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
							item.old_owner = owner.user
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
					task = Task.objects.select_for_update().filter(task_params='[["%s"], {}]' % item_id)
					task.delete()

					owner.balance += amount
					owner.income += amount
					owner.save()

					person.balance -= amount
					person.expenses += amount
					person.save()

			

			if item.state == 'sold':
				SockConsumer.broadcast({
					"op": "item_view_change",
					"item": item.table_sell_item(),
					"action": "ended"
					})
				SockConsumer.broadcast({
					"op": "item_sold",
					"item_id": item.id,
					"owner": str(item.owner)
					})

				notf_records = UserNotification.objects.filter(item_id=item.id)
				users = [obj.user.id for obj in notf_records]
				SockConsumer.send_notification(users, { 
					"op": "notification",
					"message": "{} bid {} to item {}. Auction of {} ended. Winner is {}".format(person.user.username, amount, item.title, item.title, item.owner)
				})
			else:
				notf_records = UserNotification.objects.filter(item_id=item.id)
				users = [obj.user.id for obj in notf_records]
				SockConsumer.send_notification(users, { 
					"op": "notification",
					"message": "{} bid {} to item {}. Highest bidder {}".format(person.user.username, amount, item.title, item.current_bidder)
				})

			SockConsumer.broadcast({
				"op": "bid_record_add",
				"item_id": item.id,
				"bidder":str(request.user),
				"amount": amount,
				"created_at": str(BidRecord.objects.get(bidder=request.user, 
										bidder_name=request.user.username, 
										item=item, amount=amount).created_at)
			})
			SockConsumer.broadcast({
				"op": "item_view_change",
				"item": item.table_add_bid()
			})

			# USER CHANGES
			SockConsumer.broadcast({
				"op": "user_change",
				"u": Person.objects.get(user = item.owner).table_user()
			})
			if item.old_owner:
				SockConsumer.broadcast({
					"op": "user_change",
					"u": Person.objects.get(user = item.owner).table_user()
				})
			if item.current_bidder:
				SockConsumer.broadcast({
					"op": "user_change",
					"u": Person.objects.get(user = item.current_bidder).table_user()
				})
			return JsonResponse({"status":"OK","msg":"Bid!"})


@login_required
def sell_item(request,item_id):
	with transaction.atomic():
		task = Task.objects.select_for_update().filter(task_params='[["%s"], {}]' % item_id)
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
				person.expenses += item.current_value
				person.save()
			owner = Person.objects.get(user=item.owner)
			owner.balance += item.current_value
			owner.income += item.current_value
			owner.save()
			item.owner = item.current_bidder
		item.state = 'sold'
		item.auction_ended_at = datetime.datetime.now()
		item.save()
	
	SockConsumer.broadcast({
		"op": "item_view_change",
		"item": item.table_sell_item(),
		"action": "ended"
		})
	SockConsumer.broadcast({
		"op": "delete_button",
		"item_id": item.id,
		"owner": str(item.owner)
	  })
	SockConsumer.broadcast({
			"op": "user_change",
			"u": Person.objects.get(user = item.owner).table_user()
		})
	if item.old_owner:
		SockConsumer.broadcast({
			"op": "user_change",
			"u": Person.objects.get(user = item.owner).table_user()
		})
	SockConsumer.broadcast({
		"op": "user_change",
		"u": item.owner.table_user()
	})
	if item.old_owner:
		SockConsumer.broadcast({
			"op": "user_change",
			"u": item.old_owner.table_user()
		})

	notf_records = UserNotification.objects.filter(item_id=item_id)
	users = [obj.user.id for obj in notf_records]
	SockConsumer.send_notification(users, { 
		"op": "notification",
		"message": "Auction of {} ended. Winner is {}".format(item.title, item.owner)
	})
	return JsonResponse({"msg": "sell item button is pressed!"})

@login_required
def delete_item(request,item_id):
	item = SellItem.objects.get(id=item_id)
	if not item.owner_id == request.user.id:
		return view_item(request,item_id)
	if item.state == 'active':
		return view_item(request,item_id,"ACTIVE ITEMS CAN NOT BE DELETED")
	
	item.delete()
	SockConsumer.broadcast({
		"op": "item_deleted",
		"item_id": item.id
	})
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
				_auction_type["starting"] = int(auction_type[3])
				starting = int(auction_type[3])

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
				starting = 0

			_auction_type = json.dumps(_auction_type)

			SellItem.objects.create(
				owner=owner, title=title, itemtype=itemtype,
				description=description, auction_type=_auction_type,
				image=image, current_value=starting
			)
	
			message = "SellItem Created with title:{}".format(title)
			
			return redirect('/ciftlikbank')
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

def user_watch(request):
	if request.method == "POST":
		itemtype = request.POST.get("itemtype")
		UserNotification.objects.create(user=request.user, message="message",
							notification_type='user', itemtype=itemtype)
		
	return JsonResponse({"msg": "Registered to itemtype => {}".format(itemtype)})

def item_watch(request, item_id):
	UserNotification.objects.create(user=request.user, message="message",
						notification_type='user', item_id=item_id)
	return JsonResponse({"msg": "Registered to itemid => {}".format(item_id)})
