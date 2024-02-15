from datetime import datetime
from django import template

register = template.Library()

@register.filter
def convert_epoch(value):
    if value is None or value == "":
        return ""  # or you can return any default value
    try:
        return datetime.fromtimestamp(int(value)).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return value  # return the original value if conversion fails

@register.filter(name='zip')
def zip_lists(a, b):
    return zip(a, b)