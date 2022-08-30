from typing import Tuple, List

from django.http import HttpResponseRedirect
from django.urls import reverse

from drinkman.models import Stock, Transaction, Location, User, Item, Discount


def cents_to_eur(cents):
    return round((cents / 100), 2)


def set_stock(location, item, amount):
    stock, created = Stock.objects.get_or_create(location=location, item=item)
    stock.amount = amount
    stock.save()


def increase_stock(location, item, amount=1):
    stock, created = Stock.objects.get_or_create(location=location, item=item)
    stock.amount = stock.amount + amount
    stock.save()


def new_transaction(msg, user, item=None, amount=None, location=None):
    t = Transaction(user=user, message=msg, item=item, amount=amount, location=location)
    t.save()


def calc_price(item: Item, user: User) -> Tuple[int, List[Discount]]:
    discounts = Discount.objects.all()

    price = item.price
    applied_discounts = []

    if not user.is_guest:
        # Apply all discounts that can be applied
        for discount in discounts:
            if discount.balance >= discount.reduce_step:
                if price - discount.reduce_step >= 0:
                    price -= discount.reduce_step
                    applied_discounts.append(discount)

    return price, applied_discounts


def buy(user, item, location_id):
    location = Location.objects.get(id=location_id)

    if location is None:
        return None

    price, discounts = calc_price(item, user)

    new_transaction("Bought item {} for {} cents @ {}".format(item.name, price, location.name), user, item, -price,
                    location)

    user.balance -= price
    item.purchases += 1

    for discount in discounts:
        discount.balance -= discount.reduce_step
        discount.save()

    item.save()
    user.save()

    increase_stock(location, item, -1)

    return price


def refund(user, item, location_id):
    location = Location.objects.get(id=location_id)

    if location is None:
        return None

    price, discounts = calc_price(item, user)

    new_transaction("Refunded item {} for {} cents @ {}".format(item.name, price, location.name), user, item, price,
                    location=location)

    user.balance += price
    item.purchases -= 1

    for discount in discounts:
        discount.balance += discount.reduce_step
        discount.save()

    user.save()
    item.save()

    increase_stock(location, item, 1)

    return -price


def get_location(request):
    return request.COOKIES.get('location')


def redirect_qd(viewname, *args, qd=None, **kwargs):
    rev = reverse(viewname, *args, kwargs=kwargs)
    if qd:
        rev = '{}?{}'.format(rev, qd.urlencode())
    return HttpResponseRedirect(rev)


def deposit(user, amount, location_id, transaction=True):
    location = Location.objects.get(id=location_id)

    if transaction:
        new_transaction("Deposited {:12.2f} EUR @ {}".format(amount/100, location.name),
                        user, None, amount, location)

    user.balance += amount
    user.save()

    return True


def remove_empty_stocks(location_id):
    stocks = Stock.objects.all().filter(amount=0, location_id=location_id)

    for stock in stocks:
        stock.delete()


def receive_delivery(location_id, user_id, items, overwrite):
    location = Location.objects.get(id=location_id)
    log = "Added delivery @ {}".format(location)
    user = User.objects.get(id=user_id)
    for item_id, amount in items:
        item = Item.objects.filter(id=item_id).first()

        if amount != 0 or overwrite:
            if overwrite:
                set_stock(location, item, amount)
            else:
                increase_stock(location, item, amount)

            log = log + "  {}{} {}".format('=' if overwrite else '+', amount, item)

    remove_empty_stocks(location_id)

    new_transaction(log, user, location=location)


def transfer_money(from_id, to_id, amount, location_id):
    location = Location.objects.get(id=location_id)

    if location is None:
        return None

    cents = round(amount * 100)

    ufrom = User.objects.get(id=from_id)
    uto = User.objects.get(id=to_id)

    deposit(ufrom, -cents, location_id, transaction=False)
    deposit(uto, cents, location_id, transaction=False)

    new_transaction("Transferred {} EUR to {}".format(amount, uto.username), ufrom, location=location)
    new_transaction("Received {} EUR from {}".format(amount, ufrom.username), uto, location=location)
