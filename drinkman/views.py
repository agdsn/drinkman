from django.contrib import messages
from django.http import QueryDict, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from drinkman import helpers
from drinkman.forms import DeliveryForm, StockForm, UserForm
from drinkman.helpers import increase_stock, new_transaction, get_location, redirect_qd, set_stock
from drinkman.models import User, Item, Location, Stock, Transaction


def index(request):
    return render(request, 'index.html')


def users(request):
    location = request.GET.get('location')

    context = {'users': User.objects.order_by('-balance').all()}

    response = render(request, 'users.html', context)

    if location is not None:
        response.set_cookie('location', location)
    elif get_location(request) is None:
        redirect('location_select')

    return response


def user_show(request, user_id):
    user = User.objects.get(id=user_id)

    after_transaction = request.GET.get('after_transaction')

    stocks = Stock.objects.filter(location__id=get_location(request)).order_by('-amount')
    items = []

    for stock in stocks:
        items.append({'item': stock.item, 'stock': stock})

    deposits = [-1, 1, 5, 10, 20, 50]

    context = {'items': items,
               'user': user,
               'after_transaction': after_transaction,
               'deposits': deposits}

    if user.balance < 0:
        messages.error(request, "Warning! Your balance is negative. Please deposit!", "danger")

    return render(request, "user.html", context)


def item_buy(request, user_id, item_id):
    # get item that was bought
    item = Item.objects.get(id=item_id)

    # the user who bought the item
    user = User.objects.get(id=user_id)

    if helpers.buy(user, item, get_location(request)):
        messages.success(request,
                         'Successfully bought {} for {} EUR. <a href="{}">Undo Transaction</a>'
                         .format(item.name, item.get_price(),
                                 reverse('refund', kwargs={'user_id': user.id, 'item_id': item.id})))
    else:
        messages.error(request, 'Error while purchasing.')

    qd = QueryDict(mutable=True)
    qd['after_transaction'] = True

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
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.image_url = form.cleaned_data['image_url']

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
    items = Item.objects.order_by('name').all()

    if request.method == 'POST':
        form = DeliveryForm(items, request.POST)
        if form.is_valid():
            overwrite = form.cleaned_data['set']
            location = Location.objects.get(id=form.cleaned_data['location'])
            log = "Added delivery @ {}".format(location)
            user = User.objects.get(id=form.cleaned_data['user'])
            for field in form.fields:
                if field.startswith("item_"):
                    item = Item.objects.filter(id=field.split("_")[1]).first()
                    amount = form.cleaned_data[field]

                    if amount > 0 or overwrite:
                        if overwrite:
                            set_stock(location, item, amount)
                        else:
                            increase_stock(location, item, amount)

                        log = log + "  {}{} {}".format('=' if overwrite else '+', amount, item)
            new_transaction(log, user)
            return redirect('stock')

    else:
        form = DeliveryForm(items)

    return render(request, 'delivery.html', {'form': form})


def refund(request, user_id, item_id):
    # get item that was bought
    item = Item.objects.get(id=item_id)

    # the user who bought the item
    user = User.objects.get(id=user_id)

    if helpers.refund(user, item, get_location(request)):
        messages.warning(request,
                         'Successfully refunded {} for {} EUR.'
                         .format(item.name, item.get_price()))
    else:
        messages.error(request, 'Error while refunding.')

    qd = QueryDict(mutable=True)
    qd['after_transaction'] = True

    return redirect_qd('user_show', qd=qd, user_id=user_id)


def transactions_json(request, user_id):
    transactions = Transaction.objects.filter(user_id=user_id).order_by('-date').all()

    return JsonResponse([{'message': t.message, 'date': t.date.isoformat(' ', "minutes")} for t in transactions],
                        safe=False)
