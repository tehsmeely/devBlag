from django.conf.urls import patterns, include, url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^posts', views.post_list),
    url(r'^project/(?P<pid>[0-9]+)/$', views.projectPosts),
]



