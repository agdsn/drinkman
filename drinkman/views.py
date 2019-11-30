from django.http import HttpResponse
from django.shortcuts import render, redirect

from drinkman.forms import DeliveryForm
from drinkman.helpers import increase_stock, new_transaction
from drinkman.models import User, Item, Location


def index(request):
    return render(request, 'index.html')


def users(request):
    context = {'users': User.objects.all()}
    return render(request, 'users.html', context)


def user(request, user_id):
    return HttpResponse("Hello, world. You're at the polls index.")


def stock(request):
    return HttpResponse("Take a look on the current stocks...")


def delivery(request):
    items = Item.objects.all()

    if request.method == 'POST':
        form = DeliveryForm(items, request.POST)
        if form.is_valid():
            location = Location.objects.get(id=form.cleaned_data['location'])
            log = "Added delivery @ {}".format(location)
            user = User.objects.get(id=form.cleaned_data['user'])
            for field in form.fields:
                if field.startswith("item_"):
                    item = Item.objects.filter(id=field.split("_")[1]).first()
                    amount = form.cleaned_data[field]
                    increase_stock(location, item, amount)
                    log = log + "  +{} {}".format(amount, item)
            new_transaction(log, user)
            return redirect('stock')

    else:
        form = DeliveryForm(items)

    return render(request, 'delivery.html', {'form': form})
