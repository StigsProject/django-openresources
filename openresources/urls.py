# -*- coding: utf-8 -*-


# Copyright 2011 Florian Ledermann <ledermann@ims.tuwien.ac.at>
# 
# This file is part of OpenResources
# https://bitbucket.org/floledermann/openresources/
# 
# OpenResources is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# OpenResources is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with OpenResources. If not, see <http://www.gnu.org/licenses/>.


from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

from openresources import views

from openresources.models import Tag

# commenting out autocomplete stuff for now, probably needs custom implementation
#from autocomplete.views import autocomplete

#autocomplete.register(
#    id = 'keys',
#    queryset = Tag.objects.values('key').distinct(),
#    fields = ('key',),
#    limit = 20,
#    key = 'key',
#    label = 'key',
#)


view_patterns = patterns('',
    url(r'^$', views.view, name='openresources_view'),
    url(r'^view/(?P<name>[0-9A-Za-z-_]+)/json/$', views.view_json, name='geojson'),
    url(r'^view/(?P<name>[0-9A-Za-z-_]+)/(?P<mode>.*)/$', views.view, name='openresources_view'),
    url(r'^view/(?P<name>[0-9A-Za-z-_]+)/$', views.view, name='openresources_view'),
)

urlpatterns = patterns('',

    url(r'^views/$', views.views, name='openresources_views'),
    url(r'^views/new/$', views.edit_view, name='openresources_new_view'),
    url(r'^views/edit/(?P<name>[0-9A-Za-z-_]+)/$', views.edit_view, name='openresources_edit_view'),

    url(r'^templates/$', views.templates, name='openresources_templates'),
    url(r'^templates/new/$', views.edit_template, name='openresources_template_edit'),
    url(r'^template/(?P<name>[0-9A-Za-z-_]+)/$', views.edit_template, name='openresources_template_edit'),
    # temporary, until resource view support assigned template
    url(r'^template-resource/(?P<template>[0-9A-Za-z-_]+)/(?P<resource>[0-9A-Za-z-_]+)/$', views.edit_with_template, name='openresources_edit_with_template'),
    url(r'^template-resource/(?P<template>[0-9A-Za-z-_]+)/$', views.edit_with_template, name='openresources_edit_with_template'),

    #url(r'^all/$', views.all_resources, name='openresources_all'),
   
    url(r'^tags/$', views.tags, name='openresources_tags'),
    # *? matches key non-greedy, matching only as few as possible characters if value has = sign in it
    url(r'^tag/(?P<key>.*?)=(?P<value>.*)/$', views.tag, name='openresources_tag'),
    url(r'^tag/(?P<key>.*)/$', views.tag, name='openresources_tag_key'),
    url(r'^tools/rename_tag/$', views.rename_tag, name='openresources_rename_tag'),

    url(r'^icons/$', views.icons, name='openresources_icons'),
    url(r'^icons/add/$', views.add_icon, name='openresources_new_icon'),

    url(r'^choices.json$', views.resource_choices),
    url(r'^tag/(?P<key>.*)/choices.json$', views.tag_choices),
        
    # *? matches key non-greedy, matching only as few as possible characters if value has '=' sign in it
    url(r'^with/tag/(?P<key>.*?)=(?P<value>.*)/$', views.resources_by_tag, name='openresources_with_tag'),
    url(r'^with/tag/(?P<key>.*)/$', views.resources_by_tag, name='openresources_with_key'),
    url(r'^resource/(?P<key>.*)/$', views.resource, name='openresources_resource'),
    url(r'^new/$', views.edit_resource, name='openresources_new'),
    url(r'^edit/(?P<key>.*)/$', views.edit_resource, name='openresources_edit'),
    #url('^autocomplete/(\w+)/$', autocomplete, name='autocomplete'),

    url(r'^context/set/$', views.set_context, name='openresources_set_context'),
    url(r'^search/$', views.search, name='openresources_search'),
    url(r'^credits/$', direct_to_template, {'template': 'openresources/credits.html'}, name='openresources_credits'),

    url(r'^json/all/$', views.all_json, name='geojson_all'),

    url(r'^in/(?P<area>[0-9A-Za-z-_]+)/', include(view_patterns)),
    url(r'^', include(view_patterns)),

    # this cannot be reached, as we show the default view as an index page
    # however this is used for reversing the index page url in templates
    url(r'^$', views.index, name='openresources_index'),

)
