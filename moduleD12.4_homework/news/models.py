from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models import Sum


class Author(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    author_rating = models.IntegerField(default=0)

    def update_rating(self):
        # суммарный рейтинг каждой статьи автора умножается на 3;
        author_posts_rating = self.post_set.aggregate(Sum('news_rating')).get('news_rating__sum')
        # суммарный рейтинг всех комментариев автора;
        author_comments = self.author.comment_set.aggregate(Sum('comment_rating')).get('comment_rating__sum')
        # суммарный рейтинг всех комментариев к статьям автора
        comments_to_posts = Comment.objects.filter(comment_post_connect__post_author=self).aggregate(Sum('comment_rating')).get('comment_rating__sum')

        if author_posts_rating is None:
            author_posts_rating = 0
        if author_comments is None:
            author_comments = 0
        if comments_to_posts is None:
            comments_to_posts = 0

        self.author_rating = author_posts_rating*3 + author_comments + comments_to_posts

        self.save(update_fields=['author_rating'])

    def __str__(self):
        return f'{self.author}'


class Category(models.Model):
    category_name = models.CharField(max_length=255,
                                     unique=True)
    subscribers = models.ManyToManyField(User, through='UserCategory')

    def __str__(self):
        return f'{self.category_name.title()}'


class UserCategory(models.Model):
    user_connect = models.ForeignKey(User, on_delete=models.CASCADE)
    subcategory_connect = models.ForeignKey(Category, on_delete=models.CASCADE)


class Post(models.Model):
    post_author = models.ForeignKey(Author, on_delete=models.CASCADE)
    news_title = models.CharField(max_length=255)
    news_text = models.TextField()
    news_rating = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)

    news = 'nw'
    article = 'ar'

    NEWS_TYPE = [(news, 'Новость'),
                 (article, 'Статья')]

    news_type_choice = models.CharField(max_length=20,
                                        choices=NEWS_TYPE,
                                        default=news)

    category = models.ManyToManyField(Category, through='PostCategory')

    def like(self):
        self.news_rating += 1
        self.save(update_fields=['news_rating'])

    def dislike(self):
        self.news_rating -= 1
        self.save(update_fields=['news_rating'])

    def preview(self):
        return self.news_text[0:123] + '...'

    def get_absolute_url(self):
        return f'/news/{self.pk}'


class PostCategory(models.Model):
    post_connect = models.ForeignKey(Post, on_delete=models.CASCADE)
    category_connect = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    comment_post_connect = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_user_connect = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField()
    comment_create_date = models.DateTimeField(auto_now_add=True)
    comment_rating = models.IntegerField(default=0)

    def like(self):
        self.comment_rating += 1
        self.save(update_fields=['comment_rating'])

    def dislike(self):
        self.comment_rating -= 1
        self.save(update_fields=['comment_rating'])
