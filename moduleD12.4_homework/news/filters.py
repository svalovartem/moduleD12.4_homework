from django_filters import FilterSet, ModelChoiceFilter
from .models import *


class PostFilter(FilterSet):
    category = ModelChoiceFilter(queryset=Category.objects.all())

    class Meta:
        model = Post
        fields = {'post_author__author__username': ['icontains'],
                  'news_title': ['icontains'],
                  'news_rating': ['gt'],
                  'create_time': ['gt'],
                  'category': []}
