from django.conf.urls import patterns, include, url

import session_csrf
session_csrf.monkeypatch()


from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'scaffold.views.home', name='home'),

    #devBlag URLS
    url(r'^', include('devBlag.urls')),
    url(r'', include('djangae.contrib.gauth.urls')),
    url(r'^_ah/', include('djangae.urls')),

    # Note that by default this is also locked down with login:admin in app.yaml
    url(r'^admin/', include(admin.site.urls)),
)
