from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    pass


# Class for posts
class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(blank=False)
    date_added = models.DateTimeField(auto_now_add=True)
    number_followers = models.IntegerField(default=0)
    likes = models.ManyToManyField("Likes", related_name="post_likes")

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


# Class for adding Likes to a Post
class Likes(models.Model):
    liking_user = models.ForeignKey(User, related_name="liking_user", on_delete=models.CASCADE)
    liked_post = models.ForeignKey(Post, related_name="liked_post", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['liking_user', 'liked_post'], name='only_like_once')
        ]