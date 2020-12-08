from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    pass


# Class for posts
class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(blank=False)
    likes = models.ManyToManyField(User, related_name='post_likes')
    date_added = models.DateTimeField(auto_now_add=True)
    number_followers = models.IntegerField(default=0)

    def likes_count(self):
        return self.likes.count()


# Class for users following other users
class UserFollowing(models.Model):
    user_id = models.ForeignKey("User", related_name="following", on_delete=models.CASCADE)
    following_user_id = models.ForeignKey("User", related_name="followers", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'following_user_id'], name='only_follow_once')
        ]