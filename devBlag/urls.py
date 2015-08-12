from django.conf.urls import patterns, include, url
from . import views


urlpatterns = [
    url(r'^$', views.index),
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^project/(?P<pid>[0-9]+)/$', views.projectPosts),
    url(r'^developer/(?P<did>[0-9]+)/$', views.developerProfile),
    url(r'^post/(?P<postID>[0-9]+)/$', views.viewPost),
    url(r'^publishPost/$', views.publishPost),
    url(r'^deletePost/$', views.deletePost),
    url(r'^addPost/(?P<projectID>[0-9]+)/(?P<postID>[0-9]+|new)/$', views.addPost),
    url(r'^profile/$', views.profile),
    #url(r'^updateProfile/$', views.updateProfile),
    url(r'^createProject/(?P<projectID>[0-9]+|new)/$', views.createProject),
    url(r'^deleteProject/$', views.deleteProject),
    url(r'^addResource/$', views.addResource),
    url(r'^getResources/$', views.getResources2),
    url(r'^deleteResource/$', views.deleteResource),
    url(r'^devApply/$', views.developerApply),
    url(r'^becomeDeveloper/$', views.createDeveloper),
    ## AJAX editing routes
    url(r'^ajaxRouting/updateProfile/$', views.updateProfile),
    url(r'^ajaxRouting/getPosts/$', views.getPosts),
    ##  Test URLs:
    url(r'^test/jqUIdialogs/$', views.dialogTest),
]



