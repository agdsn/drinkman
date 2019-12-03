from django import template

register = template.Library()


@register.filter
def divi(value, arg):
    return int(value) / arg
