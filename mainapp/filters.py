import django_filters
from django.db import models
from django import forms

from blogapp.models import SNPosts


class PostsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super(PostsFilter, self).__init__(data=data, queryset=queryset, request=request, prefix=prefix)
        self.filters['name'].field.widget.attrs.update({'class': 'custom-search'})

    class Meta:
        model = SNPosts
        fields = ['name']
        widgets = {
            'name': django_filters.CharFilter(attrs={'class': 'form-control'})
        }


