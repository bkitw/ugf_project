from django import template
from urllib.parse import urlencode
from django.utils.timezone import activate
from django.conf import settings
from pytz import timezone


activate(settings.TIME_ZONE)
register = template.Library()


@register.filter
def format_datetime(value):
    settings_time_zone = timezone(settings.TIME_ZONE)
    value = value.astimezone(settings_time_zone)
    value = value.strftime('%H:%M, %d-%m-%Y')
    return value
