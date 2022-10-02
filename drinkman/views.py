import datetime
import re

import pytz
from django.contrib import messages
from django.db.models import Count, Func, OuterRef, Subquery
from django.db.models.functions import Lower
from django.http import QueryDict, JsonResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from drinkman import helpers
from drinkman.forms import DeliveryForm, StockForm, UserForm, TransferForm
from drinkman.helpers import increase_stock, new_transaction, get_location, redirect_qd, set_stock, receive_delivery, \
    transfer_money, cents_to_eur
from drinkman.models import User, Item, Location, Stock, Transaction


def index(request):
    return render(request, 'index.html')


def users(request):
    location_id = request.GET.get('location')

    setcookie = False

    if location_id is None:
        location_id = get_location(request)
    else:
        setcookie = True

    if location_id is None:
        return redirect('locations')

    daysago30 = datetime.datetime.utcnow() - datetime.timedelta(days=30)
    last_user_ids_q = Transaction.objects.filter(user_id=OuterRef('id'), date__gte=daysago30,
                                                 location_id=location_id).values('user_id').distinct()

    users_recent = list(User.objects.order_by(Lower('username')).filter(id__in=Subquery(last_user_ids_q)).all())
    users_other = list(User.objects.order_by(Lower('username')).exclude(id__in=Subquery(last_user_ids_q)).all())

    users_recent.sort(key=lambda user: re.sub(r'[^a-z0-91]+', '', user.username.lower()))
    users_other.sort(key=lambda user: re.sub(r'[^a-z0-91]+', '', user.username.lower()))

    context = {'users_recent': users_recent, 'users_other': users_other}

    response = render(request, 'users.html', context)

    if setcookie:
        response.set_cookie('location', location_id)

    return response


def user_show(request, user_id):
    user = User.objects.get(id=user_id)

    after_transaction = request.GET.get('after_transaction')

    user_item_purchases_raw = Transaction.objects \
        .values('item__id') \
        .annotate(purchases=Count('item')) \
        .filter(user=user,
                amount__lt=0)

    user_item_purchases = {
        uip['item__id']: uip['purchases']
        for uip in user_item_purchases_raw
    }

    stockitems = []
    available_stocks = list(Stock.objects.filter(location__id=get_location(request), amount__gt=0).order_by(
        '-item__purchases', 'item__name'))

    available_stocks.sort(key=lambda si: user_item_purchases.get(si.item.id, 0), reverse=True)

    for available_stock in available_stocks:
        stockitems.append({'item': available_stock.item, 'stock': available_stock})

    not_available_stocks =Stock.objects.filter(location__id=get_location(request), amount__lte=0).order_by(
        '-item__purchases', 'item__name')
    for not_available_stock in not_available_stocks:
        stockitems.append({'item': not_available_stock.item, 'stock': not_available_stock})

    deposits = [-1, 1, 5, 10, 20, 50]

    context = {'stockitems': stockitems,
               'user': user,
               'after_transaction': after_transaction,
               'deposits': deposits}

    if user.balance < 0:
        messages.error(request, "Warning! Your balance is negative. Please deposit! Maximum negative balance is -10€.",
                       "danger")

    if user.is_guest:
        messages.info(request, "This is the guest user. Please select an item and deposit the shown amount of money in cash.")

    return render(request, "user.html", context)


def item_buy(request, user_id, item_id):
    # get item that was bought
    item = Item.objects.get(id=item_id)

    # the user who bought the item
    user = User.objects.get(id=user_id)

    transaction = Transaction.objects.filter(user=user).order_by("-date").first()

    qd = QueryDict(mutable=True)
    qd['after_transaction'] = True

    utc_now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

    wait_seconds = 2

    if transaction is None or (utc_now - transaction.date) > datetime.timedelta(seconds=wait_seconds):
        price = helpers.buy(user, item, get_location(request))
        if price is not None:
            messages.success(request,
                             'Successfully bought {} for {:12.2f} EUR. <a href="{}">Undo Transaction</a>'
                             .format(item.name, cents_to_eur(price),
                                     reverse('refund', kwargs={'user_id': user.id, 'item_id': item.id})))
        else:
            messages.error(request, 'Error while purchasing.')
    else:
        messages.error(request, f'Please wait {wait_seconds} seconds between actions.', )

    return redirect_qd('user_show', qd=qd, user_id=user_id)


def deposit(request, user_id, amount):
    user = User.objects.get(id=user_id)

    if helpers.deposit(user, amount * 100, get_location(request)):
        messages.success(request, 'Successfully deposited {} EUR.'.format(amount))
    else:
        messages.error(request, 'Error while depositing.')

    qd = QueryDict(mutable=True)
    qd['after_transaction'] = True

    return redirect_qd('user_show', qd=qd, user_id=user_id)


def user_new(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = User(username=form.cleaned_data['username'], email=form.cleaned_data['email'],
                        image_url=form.cleaned_data['image_url'])
            user.save()
            return redirect('users')
    else:
        form = UserForm()

    return render(request, 'new_user.html', {'form': form})


def user_edit(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            image_url = form.cleaned_data['image_url']

            new_transaction("Edited user: {}<{}> -> {}<{}>".format(user.username, user.email, username, email), user)

            user.username = username
            user.email = email
            user.image_url = image_url

            user.save()

            messages.success(request, "Changes saved.")

            return redirect('user_show', user_id=user.id)
    else:
        form = UserForm(data={'username': user.username, 'email': user.email, 'image_url': user.image_url})

    return render(request, 'edit_user.html', {'form': form, 'user': user})


def location_select(request):
    context = {'locations': Location.objects.all()}
    return render(request, "location_select.html", context)


def stock(request):
    location_id = request.GET.get('location', 1)

    form = StockForm()

    context = {
        'location_id': location_id,
        'form': form
    }

    return render(request, 'stock.html', context)


def delivery(request):
    items = Item.objects.order_by('name').all()

    if request.method == 'POST':
        form = DeliveryForm(items, request.POST)
        if form.is_valid():
            items = []
            for field in form.fields:
                if field.startswith("item_"):
                    items.append((field.split("_")[1], form.cleaned_data[field]))

            receive_delivery(form.cleaned_data['location'], form.cleaned_data['user'], items, form.cleaned_data['set'])

            return redirect('stock')
    else:
        form = DeliveryForm(items)

    return render(request, 'delivery.html', {'form': form})


def refund(request, user_id, item_id):
    # get item that was bought
    item = Item.objects.get(id=item_id)

    # the user who bought the item
    user = User.objects.get(id=user_id)

    refund_amt = helpers.refund(user, item, get_location(request))

    if refund_amt is not None:
        messages.warning(request,
                         'Successfully re-pfanded {} for {:12.2f} EUR.'
                         .format(item.name, cents_to_eur(refund_amt)))
    else:
        messages.error(request, 'Error while re-pfanding.')

    qd = QueryDict(mutable=True)
    qd['after_transaction'] = True

    return redirect_qd('user_show', qd=qd, user_id=user_id)


def transactions_json(request, user_id):
    transactions = Transaction.objects.filter(user_id=user_id).order_by('-date').all()

    return JsonResponse([{'message': t.message, 'date': t.date.isoformat(' ', "minutes")} for t in transactions],
                        safe=False)


def stock_json(request, location_id):
    stock = Stock.objects.order_by('item__name')

    if location_id is not None:
        stock = stock.filter(location_id=location_id)

    stock = stock.all()

    return JsonResponse([{'item': st.item.name,
                          'location': st.location.name,
                          'amount': st.amount} for st in stock],
                        safe=False)


def transfer(request, user_id):
    form = TransferForm(request.POST)

    if form.is_valid():
        transfer_money(user_id, form.cleaned_data['to_user'], form.cleaned_data['amount'], get_location(request))

        messages.success(request, "Balance transferred.")

        return redirect('user_show', user_id=user_id)

    return render(request, 'transfer.html', {'form': form, 'user_id': user_id})
