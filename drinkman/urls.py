"""drinkman URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, register_converter

from drinkman import views, converters

register_converter(converters.NegativeIntConverter, 'negint')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),

    path('users/', views.users, name='users'),
    path('users/<int:user_id>', views.user_show, name='user_show'),
    path('users/<int:user_id>/edit', views.user_edit, name='user_edit'),
    path('users/new', views.user_new, name='user_new'),
    path('users/<int:user_id>/buy/<int:item_id>', views.item_buy, name='item_buy'),
    path('users/<int:user_id>/deposit/<negint:amount>', views.deposit, name='deposit'),
    path('users/<int:user_id>/transactions/json', views.transactions_json, name='transactions_json'),
    path('users/<int:user_id>/transfer', views.transfer, name='transfer'),

    path('stock/<int:location_id>/json/', views.stock_json, name='stock_json'),
    path('stock/', views.stock, name='stock'),

    path('delivery/', views.delivery, name='delivery'),

    path('locations/', views.location_select, name='locations'),

    path('users/<int:user_id>/refund/<int:item_id>', views.refund, name='refund'),
]
