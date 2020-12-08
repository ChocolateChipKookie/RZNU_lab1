"""lab_1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import re_path, path, include
from lab_1.rest_api import views


urlpatterns = [
    # Users
    re_path('^users/?$', views.UsersView.as_view(), name='user-list'),
    path('users/<username>', views.UsersView.UserView.as_view(), name='user-detail'),
    # Follow
    path('follow/<username>', views.UsersView.FollowView.as_view(), name='follow'),

    # Posts
    path('post', views.PostsView.NewPostView.as_view(), name='new-post'),
    re_path('^posts/?$', views.PostsView.as_view(), name='post-list'),
    path('posts/<int:id>', views.PostsView.PostView.as_view(), name='post-detail'),
    path('posts/<username>', views.PostsView.UserPostsView.as_view(), name='posts-user-list'),
]
