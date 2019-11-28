from django.http import HttpResponse
from django.shortcuts import render

from drinkman.models import User


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def users(request):
    context = {'users': User.objects.all()}
    return render(request, 'users.html', context)


def user(request, user_id):
    return HttpResponse("Hello, world. You're at the polls index.")
