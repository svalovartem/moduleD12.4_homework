from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.models import User
from .models import *
from .filters import PostFilter
from .forms import *
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages


class NewsList(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-create_time')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class CategoryList(NewsList):
    model = Post
    template_name = 'category.html'
    context_object_name = 'cats'
    queryset = Post.objects.order_by('-create_time')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['category'] = Category.objects.get(id=self.kwargs.get('pk'))
        category = Category.objects.get(id=self.kwargs.get('pk'))
        subscribers = category.subscribers.all()
        context['is_subscribed'] = self.request.user in subscribers
        return context


@login_required
def category_subscribe(request, **kwargs):
    Category.objects.get(id=kwargs.get('pk')).subscribers.add(request.user)
    return redirect('/')


@login_required
def category_unsubscribe(request, **kwargs):
    Category.objects.get(id=kwargs.get('pk')).subscribers.remove(request.user)
    return redirect('/')


class NewsDetail(DetailView):
    model = Post
    template_name = 'newsobj.html'
    context_object_name = 'newsobj'


class SearchList(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'search'
    queryset = Post.objects.order_by('-create_time')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


class NewsCreate(PermissionRequiredMixin, CreateView):
    model = Post
    template_name = 'add.html'
    form_class = PostForm
    context_object_name = 'add'
    permission_required = ('news.post.add_post',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                Author.objects.get(author_id=request.user.id)
            except Author.DoesNotExist:
                Author.objects.create(author=User.objects.get(id=request.user.id))
            finally:

                news_title = request.POST['news_title']
                news_text = request.POST['news_text']
                category_id = request.POST['category']
                posts = Post.objects.all().filter(post_author=Author.objects.get(author_id=request.user.id)).filter(
                    create_time__date=datetime.today()).count()

                if posts < 3:
                    newpost = Post.objects.create(post_author=Author.objects.get(author_id=request.user.id),
                                                  news_title=news_title, news_text=news_text)
                    newpost.save()
                    for i in category_id:
                        cat = Category.objects.get(id=i)
                        newpost.category.add(cat)
                    newpost.save()
                else:
                    return render(request, template_name="add-denied.html")
            return super().get(request, *args, **kwargs)


class NewsUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.post.change_post',)
    model = Post
    template_name = 'edit.html'
    form_class = PostForm
    context_object_name = 'edit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')

        return Post.objects.get(id=id)


class NewsDelete(PermissionRequiredMixin, DeleteView):
    template_name = 'delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'
    permission_required = ('news.post.delete_post',)


class Posts(View):

    def get(self, request):
        news = Post.objects.order_by('-create_time')
        p = Paginator(news, 10)

        news = p.get_page(request.GET.get('page', 1))

        data = {
            'news': news,
        }
        return render(request, 'news/news.html', data)


class PostsSearch(View):

    def get(self, request):
        search = Post.objects.order_by('-create_time')
        pi = Paginator(search, 10)

        search = pi.get_page(request.GET.get('page', 1))

        data = {
            'search': search,
        }
        return render(request, 'search/search.html', data)
