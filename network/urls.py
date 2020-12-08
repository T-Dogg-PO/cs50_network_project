
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("profile/<int:requested_user_id>", views.profile, name="profile"),
    path("follow", views.follow, name="follow"),
    path("like", views.like, name="like"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
