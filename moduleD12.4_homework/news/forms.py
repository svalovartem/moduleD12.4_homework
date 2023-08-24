from django.forms import ModelForm
from .models import *
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['news_title',
                  'category',
                  'news_text']


class CustomSignupForm(SignupForm):

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return user
