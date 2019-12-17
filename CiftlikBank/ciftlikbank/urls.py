from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('home', views.index, name='home'),
    path('sell_item_create', views.sell_item_create, name='sell_item_create'),
    path('make_bid', views.make_bid, name='make_bid')
]