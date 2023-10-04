from django import template

from coolinary.models import UserProfile

register = template.Library()


@register.filter
def avatar(user):
    profile = UserProfile.objects.get_or_create(user=user)[0]
    if profile.avatar:
        return profile.avatar.url
    else:
        return '/static/svg/avatar.svg'
