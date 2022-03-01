from datetime import datetime

from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.TextField()
    balance = models.IntegerField(default=0)
    image_url = models.TextField(null=True)
    email = models.EmailField(null=True)
    hide_log = models.BooleanField(default=0)

    def __str__(self):
        return self.username

    def token(self):
        return self.username[0]

    def get_balance(self):
        return "{:12.2f}".format(round((self.balance / 100), 2))

    @property
    def fee(self):
        if self.balance < -1000:
            multiplier = abs(self.balance)

            return round(round(multiplier / 100, 2) * 0.01, 2)

        return 0

    def calc_price(self, price):
        return "{:12.2f}".format(round(((price + (price * self.fee)) / 100), 2))


class Item(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    image_url = models.TextField()
    price = models.IntegerField()
    purchases = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_price(self):
        return "{:12.2f}".format(round((self.price / 100), 2))


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()

    def __str__(self):
        return self.name


class Stock(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return "{} @{}".format(self.item.name, self.location.name)


class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    message = models.TextField()
    date = models.DateTimeField(default=datetime.now)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "{}.{}.{}".format(self.id, self.user.username, self.date)
