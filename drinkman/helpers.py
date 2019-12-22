from django.http import HttpResponseRedirect
from django.urls import reverse

from drinkman.models import Stock, Transaction, Location


def set_stock(location, item, amount):
    stock, created = Stock.objects.get_or_create(location=location, item=item)
    stock.amount = amount
    stock.save()


def increase_stock(location, item, amount=1):
    stock, created = Stock.objects.get_or_create(location=location, item=item)
    stock.amount = stock.amount + amount
    stock.save()


def decrease_stock(location, item, amount=1):
    stock, created = Stock.objects.get_or_create(location=location, item=item)
    stock.amount -= amount
    stock.save()


def new_transaction(msg, user):
    t = Transaction(user=user, message=msg)
    t.save()


def buy(user, item, location_id):
    location = Location.objects.get(id=location_id)

    if location is None:
        return False;

    new_transaction("Bought item {} for {} cents @ {}".format(item.name, item.price, location.name), user)

    user.balance -= item.price
    user.save()

    decrease_stock(location, item)

    return True


def refund(user, item, location_id):
    location = Location.objects.get(id=location_id)

    if location is None:
        return False

    new_transaction("Refunded item {} for {} cents @ {}".format(item.name, item.price, location.name), user)

    user.balance += item.price
    user.save()

    increase_stock(location, item)

    return True


def get_location(request):
    return request.COOKIES['location']


def redirect_qd(viewname, *args, qd=None, **kwargs):
    rev = reverse(viewname, *args, kwargs=kwargs)
    if qd:
        rev = '{}?{}'.format(rev, qd.urlencode())
    return HttpResponseRedirect(rev)


def deposit(user, amount, location_id):
    location = Location.objects.get(id=location_id)

    new_transaction("Deposited {} EUR @ {}".format(amount/100, location.name),
                    user)

    user.balance += amount
    user.save()

    return True
