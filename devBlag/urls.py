from django.conf.urls import patterns, include, url
from . import views


urlpatterns = [
    url(r'^$', views.index),
    url(r'^logout/$', views.logout),
    url(r'^project/(?P<pid>[0-9]+)/$', views.projectPosts),
    url(r'^developer/(?P<did>[0-9]+)/$', views.developerProfile),
    url(r'^addPost/$', views.addPost)
]



