from django import template

register = template.Library()


# проверка является ли пользователь членом группы
@register.simple_tag(name="has_group", takes_context=True)
def has_group(context, group_name):
    user = context['request'].user
    return user.groups.filter(name=group_name).exists()
