from django import template

register = template.Library()


@register.filter
def avatar(user):
    if user.userprofile and user.userprofile.avatar:
        return user.userprofile.avatar.url
    else:
        return '/static/svg/avatar.svg'
