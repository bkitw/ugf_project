import django_filters
from .models import *
from django_filters import CharFilter
from django.db.models import Q


# class UserFilter(django_filters.FilterSet):
#     username = CharFilter(field_name='username', lookup_expr='icontains')
#     first_name = CharFilter(field_name='first_name', lookup_expr='icontains')
#     last_name = CharFilter(field_name='last_name', lookup_expr='icontains')
#     email = CharFilter(field_name='email', lookup_expr='icontains')
#
#     class Meta:
#         model = CustomUser
#         fields = ['username', 'first_name', 'last_name',
#                   'email', 'gender']


class UserFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='my_custom_filter', label="Search")

    class Meta:
        model = CustomUser
        fields = ['q', 'gender']

    def my_custom_filter(self, queryset, name, value):
        return queryset.filter(
            Q(username__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(email__icontains=value)
        )
