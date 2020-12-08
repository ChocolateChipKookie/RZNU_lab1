from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    following = models.ManyToManyField('self', symmetrical=False, )

    def get_posts(self):
        return Post.objects.filter(profile=self)

    def get_posts_count(self):
        return self.get_posts().count()

    def get_following(self):
        following = User.objects.filter(id__in=self.following.values_list('user_id', flat=True)).all()
        return following

    def get_following_count(self):
        return self.get_following().count()

    def get_followers(self):
        followers = User.objects.filter(id__in=self.profile_set.all().values_list('user_id', flat=True)).all()
        return followers

    def get_followers_count(self):
        return self.get_followers().count()


class Post(models.Model):
    content = models.CharField(max_length=256)
    created = models.DateTimeField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.content
