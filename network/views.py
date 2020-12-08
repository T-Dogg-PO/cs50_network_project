from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django import forms
import json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

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

            # Setting up pagination to only show 10 posts on the page at once
            # Get all posts ordered by date added
            all_posts = Post.objects.all().order_by('-date_added')
            # Use the Paginator function to split all_posts into pages of 10
            paginator = Paginator(all_posts, 10)

            # Get the information for what page the user wants to view
            page_number = request.GET.get('page')
            # Get a page object using both the page number and the paginator above
            page_obj = paginator.get_page(page_number)

            return render(request, "network/index.html", {
                "page_obj": page_obj,
                "new_post": Create()
            })

    # Setting up pagination to only show 10 posts on the page at once
    # Get all posts ordered by date added
    all_posts = Post.objects.all().order_by('-date_added')
    # Use the Paginator function to split all_posts into pages of 10
    paginator = Paginator(all_posts, 10)

    # Get the information for what page the user wants to view
    page_number = request.GET.get('page')
    # Get a page object using both the page number and the paginator above
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "page_obj": page_obj,
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
    # Get the User object for the user who's profile is going to be looked at
    profile_user = User.objects.get(id=requested_user_id)
    # Get all of the UserFollowing objects for this user
    followers = profile_user.followers.all()
    # Count the number of followers returned so that we can display this on our page
    if followers == None:
        followers_count = 0
    else:
        followers_count = len(followers)
    
    # Check to see if the user is logged in, and if logged in user is already following the target user.
    if request.user.is_anonymous:
        existing_follow = None
    else:
        following_user = request.user
        try:
            existing_follow = UserFollowing.objects.get(user_id=following_user, following_user_id=profile_user)
        except UserFollowing.DoesNotExist:
            existing_follow = None

    # Set up True/False variable for hiding/showing the follow button
    if existing_follow != None:
        existing_follow_button = True
    else:
        existing_follow_button = False

    # Setting up pagination to only show 10 posts on the page at once
    # Get all posts ordered by date added
    all_posts = Post.objects.filter(user=profile_user).order_by('-date_added')
    # Use the Paginator function to split all_posts into pages of 10
    paginator = Paginator(all_posts, 10)

    # Get the information for what page the user wants to view
    page_number = request.GET.get('page')
    # Get a page object using both the page number and the paginator above
    page_obj = paginator.get_page(page_number)

    # Load the profile page
    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "page_obj": page_obj,
        "followers_count": followers_count,
        "existing_follow": existing_follow_button
    })


# View for loading the following of a user
@login_required
def following(request):
    # Get all of the users that this user is following from UserFollowing
    following_obj = request.user.following.all()
    # Count the number of users that we are following so that we can display this on our page
    if following_obj == None:
        following_count = 0
    else:
        following_count = len(following_obj)
        
    # Setting up pagination to only show 10 posts on the page at once
    # Get all posts that have been made by followed users, ordered by date added
    # Filter is looking for the user_id field (a field for the UserFollowing model)
    # matching id values found in following_obj above.
    following_posts = Post.objects.filter(user_id__in=following_obj.values('following_user_id')).order_by('-date_added')
    # Use the Paginator function to split all_posts into pages of 10
    paginator = Paginator(following_posts, 10)

    # Get the information for what page the user wants to view
    page_number = request.GET.get('page')
    # Get a page object using both the page number and the paginator above
    page_obj = paginator.get_page(page_number)

    # Load the profile page
    return render(request, "network/following.html", {
        "page_obj": page_obj,
        "following_count": following_count,
    })


# View for following/unfollowing, to be used by JavaScript
@login_required
def follow(request):
    # Check that the request method is PUT
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    # Load the json body into the 'data' variable
    data = json.loads(request.body)
    # Take data information and store components in relevant varaibles
    requested_following_id = data["profile"]

    # Get User objects for the person following/unfollowing, and the person being followed
    follower = request.user
    user = User.objects.get(id=requested_following_id)

    # Determine if follower is already following this profile or not
    try:
        existing_follow = UserFollowing.objects.get(user_id=follower, following_user_id=user)
    except UserFollowing.DoesNotExist:
        existing_follow = None
    
    # Either create a new UserFollowing object or delete the relevant object
    if existing_follow == None:
        UserFollowing.objects.create(user_id=follower, following_user_id=user)
    else:
        existing_follow.delete()
    
    # Get the new total followers count for this profile
    total_followers = UserFollowing.objects.filter(following_user_id=user).count()
    
    # Return the total_followers number as a JsonResponse, to be used by JavaScript to update the followers count
    # without reloading the page
    return JsonResponse({"total_followers": total_followers})


# Method for liking/unliking posts
@login_required
def like(request):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)

    data = json.loads(request.body)
    post_id = data["post"]

    post = Post.objects.get(id=post_id)

    liking_user = request.user

    user_like = False

    if post.likes.filter(id=liking_user.id).exists():
        post.likes.remove(liking_user)
        user_like = False
    else:
        post.likes.add(request.user)
        user_like = True
    
    total_likes = post.likes.all().count()

    return JsonResponse({
        "total_likes": total_likes,
        "user_like": user_like
    })


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
