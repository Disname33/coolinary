from django import template

register = template.Library()


@register.filter
def temperature(temp):
    if temp is None:
        return temp
    if isinstance(temp, (int, float)) and temp > 0:
        return f'+{temp}°C'
    if isinstance(temp, str) and not (temp.startswith("-") or temp in {"0", "0.0"}):
        return f'+{temp}°C'
    return f'{temp}°C'
