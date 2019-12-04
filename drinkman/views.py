from django.http import HttpResponse
from django.shortcuts import render, redirect

from drinkman.forms import DeliveryForm, StockForm, NewUserForm
from drinkman.helpers import increase_stock, new_transaction
from drinkman.models import User, Item, Location, Stock


def index(request):
    return render(request, 'index.html')


def users(request):
    context = {'users': User.objects.all(), "locationid": request.GET.get("location")}
    return render(request, 'users.html', context)


def user(request, user_id):
    stocks = Stock.objects.filter(location__id=request.GET.get("location"), amount__gt=0)
    items = []
    for stock in stocks:
        items.append(stock.item)
    context = {'items': items, 'user_id': user_id, "locationid": request.GET.get("location")}
    return render(request, "order.html", context)


def buy(request, user_id, item_id):
    page_to_render = ""
    # get item that was bought
    bought_item = Item.objects.get(id=item_id)

    # the user who bought the item
    user_to_update = User.objects.get(id=user_id)

    # update user balance and check if he has enough money
    if user_to_update.balance >= bought_item.price:
        user_to_update.balance -= bought_item.price
        user_to_update.save()
        # update stock in location
        stock_to_update = Stock.objects.get(item__id=item_id, location__id=request.GET.get("location"))
        stock_to_update.amount -= 1
        stock_to_update.save()
        page_to_render = "buy.html"
    else:
        page_to_render = "badbalance.html"

    context = {'item': bought_item, 'user_id': user_id, "locationid": request.GET.get("location")}
    return render(request, page_to_render, context)


def newuser(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = User(username=form.cleaned_data['username'], email=form.cleaned_data['email'])
            user.save()
            return redirect('users')
    else:
        form = NewUserForm()

    return render(request, 'newUser.html', {'form': form})


def locselect(request):
    context = {'locations': Location.objects.all()}
    return render(request, "locationselector.html", context)


def stock(request):
    stock = Stock.objects.all()
    form = StockForm(request.GET)
    if form.is_valid():
        location = Location.objects.get(id=form.cleaned_data['location'])
        stock = Stock.objects.filter(location=location)

    else:
        form = StockForm()

    context = {
        'stock': stock,
        'form': form
    }

    return render(request, 'stock.html', context)


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


def abort(request, user_id, item_id):
    # get item that was bought
    bought_item = Item.objects.get(id=item_id)

    # the user who bought the item
    user_to_update = User.objects.get(id=user_id)

    user_to_update.balance += bought_item.price
    user_to_update.save()
    # update stock in location
    stock_to_update = Stock.objects.get(item__id=item_id, location__id=request.GET.get("location"))
    stock_to_update.amount += 1
    stock_to_update.save()

    context = {'users': User.objects.all(), "locationid": request.GET.get("location")}
    return render(request, 'abort.html', context)
