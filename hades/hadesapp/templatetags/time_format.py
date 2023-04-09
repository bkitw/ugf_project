import pytz
from django import template
from urllib.parse import urlencode
from django.utils.timezone import activate
from pytz import timezone

register = template.Library()


@register.filter
def format_datetime(value):
    value = value.astimezone(pytz.timezone('Europe/Kyiv'))
    value = value.strftime('%H:%M, %d-%m-%Y')
    return value
