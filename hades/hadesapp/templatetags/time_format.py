from django import template
from urllib.parse import urlencode

register = template.Library()


@register.filter
def format_datetime(value):
    value = value.strftime('%H:%M, %d-%m-%Y')
    return value
