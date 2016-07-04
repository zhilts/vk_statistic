"""vk_fetch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from entities.views import GroupListView, PostListView, UserListView, UserLikesListView, UserTopTenView
from vk_fetch.views import main_view

import logging

logger = logging.getLogger()
logger.info('works')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^groups/$', GroupListView.as_view(), name='group-list'),
    url(r'^posts/(?P<group_id>[0-9]+)/$', PostListView.as_view(), name='post-list'),
    url(r'^users/group/(?P<group_id>[0-9]+)/$', UserListView.as_view(), name='users-by-group'),
    url(r'^users/group/(?P<group_id>[0-9]+)/as/(?P<viewer_id>[0-9]*)/$', UserListView.as_view(),
        name='users-by-group-as-user'),
    url(r'^users/(?P<post_id>[0-9]+)/post/likes$', UserLikesListView.as_view(), name='likes-by-post'),
    url(r'^top_ten/(?P<group_id>[0-9]+)/$', UserTopTenView.as_view(), name='top-ten'),
    url(r'^main$', main_view, name='main'),
]
