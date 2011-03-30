

from django.conf import settings
from django.conf.urls.defaults import *

from django.contrib.auth import views as auth_views

import os

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^media/openresources/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.split(settings.ROOT_PATH)[0], 'openresources/media')}),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    url(r'^login/$', auth_views.login, {'template_name': 'auth/login.html'}, name='auth_login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'auth/logout.html'}, name='auth_logout'),
    (r'^lang/', include('django.conf.urls.i18n')),
    (r'^', include('openresources.urls')),
)
