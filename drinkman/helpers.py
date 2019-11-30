from drinkman.models import Stock, Transaction


def increase_stock(location, item, amount):
    stock, created = Stock.objects.get_or_create(location=location, item=item)
    stock.amount = stock.amount + amount
    stock.save()


def new_transaction(msg, user):
    t = Transaction(user=user, message=msg)
    t.save()
