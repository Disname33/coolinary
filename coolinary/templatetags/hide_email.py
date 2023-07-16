from django import template

register = template.Library()


@register.filter
def hide_email(value):
    if value is not None and '@' in value:
        parts = value.split('@')
        username = parts[0]
        if len(parts) > 1:
            domain = parts[1]
        else:
            domain = '***'
        if len(username) > 1:
            hidden_username = username[0] + '***' + username[-1]
        else:
            hidden_username = '***'
        return hidden_username + '@' + domain
    else:
        return ""
