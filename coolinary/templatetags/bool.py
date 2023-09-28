from django import template

register = template.Library()


@register.filter
def bool_js(value):
    return ('false', 'true')[value]
