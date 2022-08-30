from django import template

from drinkman import helpers
from drinkman.helpers import cents_to_eur

register = template.Library()


@register.filter
def to_decimal(value):
    return "{:12.2f}".format(cents_to_eur(value))


@register.simple_tag
def calc_price(item, user):
    price, _ = helpers.calc_price(item, user)
    return price

