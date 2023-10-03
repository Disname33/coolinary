from datetime import datetime, timedelta

from django import template

register = template.Library()


@register.filter
def is_old_game(date):
    return datetime.now(date.tzinfo) - date > timedelta(minutes=20)
