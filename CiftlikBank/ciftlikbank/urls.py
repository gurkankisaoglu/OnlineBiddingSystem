from django.urls import path
from django.conf.urls import url, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('home', views.index, name='home'),
    path('sell_item_create', views.sell_item_create, name='sell_item_create'),
    path('make_bid', views.make_bid, name='make_bid'),
    url(r'^view/(?P<item_id>[0-9]+)', views.view_item),
    url(r'^view/start_auction/(?P<item_id>[0-9]+)', views.start_auction),
    url(r'^view/sell_item/(?P<item_id>[0-9]+)', views.sell_item),
    url(r'^view/bid_item/(?P<item_id>[0-9]+)', views.bid_item),

]