from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django import forms
import json
from django.contrib.auth.decorators import login_required

from .models import User, Post, UserFollowing

# Set up Django Form for submitting a new post
class Create(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control w-25'
                })
        }
        labels = {
            'content': ('')
        }


# Will take users to the 'All Posts' page. If request.method is post, submit a new Post instead
def index(request):
    if request.method == "POST":
        create_post = Create(request.POST)

        if create_post.is_valid():
            new_post = Post()
            new_post.user = request.user
            new_post.content = create_post.cleaned_data['content']
            new_post.save()

            return render(request, "network/index.html", {
                "all_posts": Post.objects.all().order_by('-date_added'),
                "new_post": Create()
            })

    return render(request, "network/index.html", {
        "all_posts": Post.objects.all().order_by('-date_added'),
        "new_post": Create()
    })


# View for editing a post to be used by JavaScript
@login_required
def edit(request, post_id):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    
    try:
        post_for_editing = Post.objects.get(user=request.user, id=post_id)
    except:
        return JsonResponse({"error": "Post not found"}, status=400)

    # json.loads converts the JSON string obtained from our JS into a usable Python dict
    data = json.loads(request.body)
    post_for_editing.content = data["content"]
    post_for_editing.save()
    return HttpResponse(status=204)


# View for loading the profile page of a user
def profile(request, requested_user_id):

    profile_user = User.objects.get(id=requested_user_id)

    followers = profile_user.followers.all()

    if followers == None:
        followers_count = 0
    else:
        followers_count = len(followers)

    following_user = request.user
    
    try:
        existing_follow = UserFollowing.objects.get(user_id=following_user, following_user_id=profile_user)
    except UserFollowing.DoesNotExist:
        existing_follow = None

    print(f'{existing_follow}')

    if existing_follow != None:
        existing_follow_button = True
    else:
        existing_follow_button = False

    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "user_posts": Post.objects.filter(user=profile_user).order_by('-date_added'),
        "followers_count": followers_count,
        "existing_follow": existing_follow_button
    })


# View for following/unfollowing, to be used by JavaScript
@login_required
def follow(request):
    

    if request.method != "PUT":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    requested_user_id = data["user_who_is_following"]
    requested_following_id = data["profile"]

    follower = request.user
    user = User.objects.get(id=requested_following_id)

    
    try:
        existing_follow = UserFollowing.objects.get(user_id=follower, following_user_id=user)
    except UserFollowing.DoesNotExist:
        existing_follow = None
    
    if existing_follow == None:
        UserFollowing.objects.create(user_id=follower, following_user_id=user)
    else:
        existing_follow.delete()
    
    total_followers = UserFollowing.objects.filter(following_user_id=user).count()
    
    return JsonResponse({"total_followers": total_followers})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
