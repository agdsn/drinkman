from django import template

register = template.Library()


@register.simple_tag
def user_price(user, price):
    return user.calc_price(price)
