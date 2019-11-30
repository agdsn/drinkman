from datetime import datetime

from django.db import models


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.TextField()
    balance = models.IntegerField()
    image_url = models.TextField()
    email = models.EmailField()


class Item(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    image = models.TextField()
    price = models.IntegerField()

    def __str__(self):
        return self.name


class Location(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()

    def __str__(self):
        return self.name


class Stock(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)


class Transaction(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateTimeField(default=datetime.now)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
