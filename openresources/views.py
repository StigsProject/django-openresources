

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


from django.template import RequestContext
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.views.generic.simple import redirect_to
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.db.models import Q

from django.core.urlresolvers import reverse, NoReverseMatch
from django.db.models import Count

from django.utils.translation import ugettext_lazy as _

from datetime import datetime, timedelta

from openresources.models import *
from openresources.forms import *
from openresources import settings

def resource(request, key):
    resource = get_object_or_404(Resource, shortname=key)
    related_tags = Tag.objects.filter(value_relation=resource).select_related('resource')
    return render_to_response('openresources/resource.html', RequestContext(request, locals()))

#@permission_required('openresources.change_resource')
@login_required
def edit_resource(request, key=None):
    resource = None
    if key:
        resource = get_object_or_404(Resource, shortname=key)
    
    if resource and resource.template:
        return edit_with_template(request, resource, resource.template)
    
    if request.method == "POST":
        form = ResourceForm(request.user, request.POST, request.FILES, instance=resource)
        if form.is_valid():
            
            if not resource:
                # new resource
                resource = form.save(commit=False)
                resource.creator = request.user
                resource.save()
                form.save_m2m()
            else:
                form.save()
                
            formset = TagFormSet(request.user, request.POST, request.FILES, instance=resource)
            if formset.is_valid():
                formset.saved_forms = []
                formset.save_existing_objects()
                tags = formset.save_new_objects(commit=False)
                for tag in tags:
                    tag.creator = request.user
                    tag.save()
                if 'action' in request.POST and request.POST['action'] == 'add_tag':
                    return redirect_to(request, reverse('openresources_edit', kwargs={'key':resource.shortname}))               
                else:
                    return redirect_to(request, reverse('openresources_resource', kwargs={'key':resource.shortname}))               
        else:
            formset = TagFormSet(request.user, instance=resource)
    else:
        form = ResourceForm(request.user, instance=resource)
        formset = TagFormSet(request.user, instance=resource)
        
        popular_tags = Tag.objects.values('key').annotate(key_count=Count('key')).filter(key_count__gt=2).order_by('key')

    tag_help = settings.TAG_HELP_LINKS

    return render_to_response('openresources/edit.html', RequestContext(request, locals()))


@login_required
def edit_with_template(request, resource=None, template=None):

    if resource and not isinstance(resource, Resource):
        resource = get_object_or_404(Resource, shortname=resource)

    if template and not isinstance(template, ResourceTemplate):
        template = get_object_or_404(ResourceTemplate, shortname=template)

    key_choices = Tag.objects.values('key').annotate(key_count=Count('key')).filter(key_count__gt=2).order_by('key')
    key_choices = [(val['key'], val['key']) for val in key_choices]

    if request.method == "POST":
        form = ResourceForm(request.user, request.POST, request.FILES, instance=resource)
        if form.is_valid():
            
            if not resource:
                # new resource
                resource = form.save(commit=False)
                resource.creator = request.user
                resource.save()
                form.save_m2m()
            else:
                form.save()

            # we have to wait until here to create the formset to be able to assign the instance
            formset = TemplateFormSet(template, request.POST, request.FILES, instance=resource,
                                        can_delete=request.user.has_perm('openresources.delete_tag'),
                                        key_choices=key_choices)

            if formset.is_valid():     
         
                formset.saved_forms = []
                formset.save_existing_objects()
                tags = formset.save_new_objects(commit=False)
                for tag in tags:
                    tag.creator = request.user
                    tag.save()

            if 'action' in request.POST and request.POST['action'] == 'add_tag':
                return redirect_to(request, reverse('openresources_edit_with_template', kwargs={'resource':resource.shortname, 'template':template.shortname}))               
            else:

                return redirect_to(request, reverse('openresources_resource', kwargs={'key':resource.shortname}))               
    else:
        if template and not resource:
            # pre-initialize template field for new resources
            form = ResourceForm(request.user, initial={'template':template})
        else:
            form = ResourceForm(request.user, instance=resource)
        formset = TemplateFormSet(template, instance=resource, can_delete=request.user.has_perm('openresources.delete_tag'), key_choices=key_choices)
    
    return render_to_response('openresources/edit_with_template.html', RequestContext(request, locals()))


def view(request, name=None, area=None, mode=None):

    # normalize default view url
    if name == 'all' and not mode:
        kwargs = {}
        if area: kwargs['area'] = area
        return HttpResponseRedirect(reverse('openresources_view', kwargs=kwargs))

    view_name = name
    if mode == 'json': return view_json(request, name)

    if name == None or name == 'all':
        is_default_view = True

    if area: area = get_object_or_404(Area, shortname=area)

    view = get_object_or_404(View, shortname=name or 'all')

    if not mode:
        # TODO: auto-discover appropriate mode?
        if view.show_map: mode = 'map'
        else: mode = 'list'

    if not mode in ['map','list','export','embed']:
        raise Http404()
    
    template = 'openresources/view_%s.html' % mode 
    
    if view.protected and not request.user.is_authenticated():
        return HttpResponse(status=403) # forbidden

    resources = view.get_resources()
    if not request.user.is_authenticated():
        resources = resources.filter(protected=False)
    
    default_ordering = '-creation_date'
    order_field = request.GET.get('order', default_ordering)
    _base_field = order_field.lstrip('-')
    if _base_field not in ['name','creation_date']:
        raise Http404
    if order_field == 'name':
        resources = resources.extra(select={'name_lower': 'lower(name)'}, order_by=['name_lower'])
    else:
        resources = resources.order_by(order_field)

    # extract tags for list display
    q = None
    for mapping in view.mappings.filter(show_in_list=True):
        q = q and q | Q(key=str(mapping.key)) or Q(key=str(mapping.key))
    
    if q:
        tags = Tag.objects.filter(q).select_related('resource').order_by('resource__shortname','key','value').values('resource_id','key','value')
    
        tags_dict = {}
        for tag in tags:
            # just append key valur pairs, will be grouped in the template
            if tag['resource_id'] in tags_dict:
                tags_dict[tag['resource_id']].append({'key': tag['key'], 'value': tag['value']})
            else:
                tags_dict[tag['resource_id']] = [{'key': tag['key'], 'value': tag['value']}]
    
        tags = tags_dict
        
        # ???
#        for resource in resources:
#            if resource.id in tags_dict:
#                setattr(resource, 'view_tags', tags_dict[resource.id])
        
    icon_mappings = view.mappings.exclude(icon=None)

    #context = _get_context(request)
    #context_form = ContextForm(instance=context)

    map_attribution = settings.MAP_ATTRIBUTION
    default_resource_icon = settings.DEFAULT_RESOURCE_ICON

    _order_field = 'name' 
    try:
        from transmeta import get_real_fieldname, get_fallback_fieldname
        _order_fallback_field = get_fallback_fieldname(_order_field)
        _order_field = get_real_fieldname(_order_field)
        if _order_field == _order_fallback_field:
            select_extra = {'%s_lower' % _order_field: 'lower(%s)' % _order_field}
        else:
            select_extra = {'%s_lower' % _order_field: "lower(coalesce(%s,'') || coalesce(%s,''))" % (_order_field, _order_fallback_field)}
    except ImportError:
        select_extra = {'%s_lower' % _order_field: 'lower(%s)' % _order_field}
    _order_by = ['feature_order','%s_lower' % _order_field]

    featured_areas = Area.objects.filter(featured=True).extra(select=select_extra, order_by=_order_by)
    featured_views = View.objects.filter(featured=True).extra(select=select_extra, order_by=_order_by)

    if not request.user.is_authenticated():
        featured_views = featured_views.filter(protected=False)

    def is_valid_bounds(bounds):
        bounds = bounds.split(',')
        if len(bounds) != 4: return False
        import re
        for coord in bounds:
            if not re.match('-?\d+\.?\d*',coord): return False
        return True

    if is_valid_bounds(request.GET.get('bounds','')):
        bounds = request.GET['bounds']
    
    return render_to_response(template, RequestContext(request, locals()))
    

def views(request):
    order_field = 'name' 
    try:
        from transmeta import get_real_fieldname, get_fallback_fieldname
        order_fallback_field = get_fallback_fieldname(order_field)
        order_field = get_real_fieldname(order_field)
        if order_field == order_fallback_field:
            select_extra = {'%s_lower' % order_field: 'lower(%s)' % order_field}
        else:
            select_extra = {'%s_lower' % order_field: "lower(coalesce(%s,'')) || lower(coalesce(%s,''))" % (order_field, order_fallback_field)}
    except ImportError:
        select_extra = {'%s_lower' % order_field: 'lower(%s)' % order_field}
    order_by = ['%s_lower' % order_field]
    views = View.objects.extra(select=select_extra, order_by=order_by)
    if not request.user.is_authenticated():
        views = views.filter(protected=False)

    return render_to_response('openresources/views.html', RequestContext(request, locals()))


#@permission_required('openresources.change_view')
@login_required
def edit_view(request, name=None):
    view = None
    if name:
        view = get_object_or_404(View, shortname=name)
    
    if request.method == "POST":
        form = ViewForm(request.user, request.POST, instance=view, prefix='view')
        if form.is_valid():
            
            if not view:
                # new view
                view = form.save(commit=False)
                view.creator = request.user
                view.save()
                form.save_m2m()
            else:
                form.save()
            
            queryformset = QueryFormSet(request.POST, instance=view, prefix='queries')
            queries_valid = queryformset.is_valid()
            if queries_valid:
                queryformset.saved_forms = []
                queryformset.save_existing_objects()
                queries = queryformset.save_new_objects(commit=False)
                for query in queries:
                    query.creator = request.user
                    query.save()
                    
            mappingformset = TagMappingFormSet(request.POST, instance=view, prefix='mappings')
            mappings_valid = mappingformset.is_valid()
            if mappings_valid:
                mappingformset.saved_forms = []
                mappingformset.save_existing_objects()
                mappings = mappingformset.save_new_objects(commit=False)
                for mapping in mappings:
                    mapping.creator = request.user
                    mapping.save()
            
            if queries_valid and mappings_valid:       
                if 'action' in request.POST and request.POST['action'] == 'add_row':
                    return redirect_to(request, reverse('openresources_edit_view', kwargs={'name':view.shortname}))               
                else:
                    return redirect_to(request, reverse('openresources_view', kwargs={'name':view.shortname}))               
        else:
            queryformset = QueryFormSet(instance=view, prefix='queries')
            mappingformset = TagMappingFormSet(instance=view, prefix='mappings')
    else:
        form = ViewForm(request.user, instance=view, prefix='view')
        queryformset = QueryFormSet(instance=view, prefix='queries')
        mappingformset = TagMappingFormSet(instance=view, prefix='mappings')
    
    popular_tags = Tag.objects.values('key').annotate(key_count=Count('key')).filter(key_count__gt=2).order_by('key')
    tag_help = settings.TAG_HELP_LINKS

    return render_to_response('openresources/view_edit.html', RequestContext(request, locals()))


def _get_context(request):

    if request.user.is_authenticated():
        if not request.user.get_profile().context:
            request.user.get_profile().context = Context()
            request.user.get_profile().save()
        return request.user.get_profile().context

    if 'context' in request.session:
        return request.session['context']
    request.session['context'] = Context()


def index(request):

    protect_attrs = {
        True: {},
        False: {'protected':False}
    }[request.user.is_authenticated()]

    order_field = 'name'
    try:
        from transmeta import get_real_fieldname, get_fallback_fieldname
        order_fallback_field = get_fallback_fieldname(order_field)
        order_field = get_real_fieldname(order_field)
        if order_field == order_fallback_field:
            select_extra = {'view_order': 'lower(%s)' % order_field}
        else:
            select_extra = {'view_order': "lower(coalesce(%s,'')) || lower(coalesce(%s,''))" % (order_field, order_fallback_field)}
    except ImportError:
        select_extra = {'view_order': 'lower(%s)' % order_field}

    featured_views = View.objects.filter(featured=True, **protect_attrs).extra(select=select_extra).order_by('view_order')
    featured_resources = Resource.objects.filter(featured=True, **protect_attrs)
    latest_resources = Resource.objects.filter(**protect_attrs).order_by('-creation_date')[:15]
    upcoming_resources = Resource.objects\
        .filter(tags__value_date__gte=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0), tags__key='start_date', **protect_attrs)\
        .extra(select={
            'start_date':"select value_date from openresources_tag where resource_id = openresources_resource.id and openresources_tag.key = 'start_date'",       
            'end_date':"select value_date from openresources_tag where resource_id = openresources_resource.id and openresources_tag.key = 'end_date'"        
        })\
        .order_by('tags__value_date')[:15]

    try:
        view_all = View.objects.get(shortname='all')
        icon_mappings = view_all.mappings.exclude(icon=None)
    except View.DoesNotExist:
        # no "all" view - we cannot provide icon mappings
        pass
    context = _get_context(request)
    context_form = ContextForm(instance=context)

    map_attribution = settings.MAP_ATTRIBUTION
    default_resource_icon = settings.DEFAULT_RESOURCE_ICON

    return render_to_response('openresources/index.html', RequestContext(request, locals()))


def tags(request):
    tags = Tag.objects.values('key').annotate(key_count=Count('key')).order_by('key')
    return render_to_response('openresources/tags.html', RequestContext(request, locals()))
     

@login_required
def tag_choices(request, key=None):
    from django.utils import simplejson as json
    from django.core.serializers.json import DateTimeAwareJSONEncoder
    
    choices = Tag.objects.filter(key=key).order_by('value').values_list('value', flat=True)
    
    values = list(choices)
    
    if len(values) > 0:    
        last = values[-1]
        for i in range(len(values)-2, -1, -1):
            if last == values[i]:
                del values[i]
            else:
                last = values[i]
    
    str = json.dumps({'choices':values}, cls=DateTimeAwareJSONEncoder, indent=2)
    
    return HttpResponse(str, mimetype='application/json')
    

@login_required
def resource_choices(request, key=None):
    from django.utils import simplejson as json
    from django.core.serializers.json import DateTimeAwareJSONEncoder
    
    choices = Resource.objects.values_list('shortname', flat=True).order_by('shortname')
    
    str = json.dumps({'choices':list(choices)}, cls=DateTimeAwareJSONEncoder, indent=2)
    
    return HttpResponse(str, mimetype='application/json')


def tag(request, key, value=None):
    
    tags = Tag.objects.filter(key=key)
    if value:
        tags = tags.filter(value=value)
    
    if request.user.is_authenticated():
        tags = tags.select_related('resource').order_by('value')
    else:
        tags = tags.select_related('resource').filter(resource__protected=False).order_by('value')
    
    return render_to_response('openresources/tag.html', RequestContext(request, locals()))


def resources_by_tag(request, key, value=None):
    
    tags = Tag.objects.filter(key=key)
    if value:
        tags = tags.filter(value=value)
    
    if request.user.is_authenticated():
        tags = tags.select_related('resource').order_by('resource__shortname')
    else:
        tags = tags.select_related('resource').filter(resource__protected=False).order_by('resource__shortname')
    
    return render_to_response('openresources/resources_by_tag.html', RequestContext(request, locals()))



@permission_required('openresources.batch_rename_tags')
def rename_tag(request):
    from django.utils.http import urlquote
    
    key = request.POST['key']
    value = request.POST.get('value', None)
    
    if value:
        tags = Tag.objects.filter(key=key, value=value)
    else:
        tags = Tag.objects.filter(key=key)

    for tag in tags:
        if value and 'new_value' in request.POST:
            tag.value = request.POST['new_value']
        if 'new_key' in request.POST:
            tag.key = request.POST['new_key']
        tag.save()
    
    if 'new_key' in request.POST:
        if 'new_value' in request.POST:    
            return redirect_to(request, reverse('openresources_tag', kwargs={'key':urlquote(request.POST['new_key']), 'value': urlquote(request.POST['new_value'])}))
        return redirect_to(request, reverse('openresources_tag_key', kwargs={'key':urlquote(request.POST['new_key'])}))

    if value:
        return redirect_to(request, reverse('openresources_tag', kwargs={'key':urlquote(key), 'value': urlquote(value)}))
    
    return redirect_to(request, reverse('openresources_tag_key', kwargs={'key':urlquote(key)}))


@login_required
def icons(request):
    
    icons = Icon.objects.all()
    return render_to_response('openresources/icons.html', RequestContext(request, locals()))


@login_required
def add_icon(request):
    if request.method == "POST":
        form = IconForm(request.POST, request.FILES)
        if form.is_valid():            
            # new icon
            icon = form.save(commit=False)
            icon.creator = request.user
            icon.save()
            form.save_m2m()
            return redirect_to(request, reverse('openresources_icons'))               
    else:
        form = IconForm()
        
    return render_to_response('openresources/icon_edit.html', RequestContext(request, locals()))


@login_required
def templates(request):
    templates = ResourceTemplate.objects.all()
    return render_to_response('openresources/templates.html', RequestContext(request, locals()))


def template(request, name):

    template = get_object_or_404(ResourceTemplate, shortname=name)
    resource = None

    form = ResourceForm(request.user)
    formset = TemplateFormSet(request.user, template)
            
    return render_to_response('openresources/template.html', RequestContext(request, locals()))


@login_required
def edit_template(request, name):
    template = get_object_or_404(ResourceTemplate, shortname=name)

    if request.method == "POST":
        form = ResourceTemplateForm(request.POST, request.FILES, instance=template)
        if form.is_valid():
            
            if not template:
                # new resource
                template = form.save(commit=False)
                template.creator = request.user
                template.save()
                form.save_m2m()
            else:
                form.save()
                
            formset = TagTemplateFormSet(request.POST, request.FILES, instance=template)
            if formset.is_valid():
                formset.saved_forms = []
                formset.save_existing_objects()
                tags = formset.save_new_objects(commit=False)
                for tag in tags:
                    tag.creator = request.user
                    tag.save()
                if 'action' in request.POST and request.POST['action'] == 'add_tag':
                    return redirect_to(request, reverse('openresources_template_edit', kwargs={'name':template.shortname}))               
                else:

                    return redirect_to(request, reverse('openresources_templates'))               
        else:
            formset = TagFormSet(request.user, instance=resource)
    else:
        form = ResourceTemplateForm(instance=template)
        formset = TagTemplateFormSet(instance=template)

    return render_to_response('openresources/template_edit.html', RequestContext(request, locals()))


def search(request):
    
    q = request.GET['q'].strip()
    results = {}

    results['resources'] = Resource.objects.filter(name__icontains=q)
    results['tags'] = Tag.objects.filter(value__icontains=q)

    from transmeta import get_real_fieldname
    fname = get_real_fieldname('name')
    results['views'] = View.objects.filter(**{'%s__icontains' % fname : q})

    import wiki
    results['pages'] = wiki.models.Article.objects.filter(content__icontains=q)

    return render_to_response('openresources/search_results.html', RequestContext(request, locals()))    


def set_context(request):

    if request.POST:
        if request.user.is_authenticated():
            profile = request.user.get_profile()
            form = ContextForm(request.POST, instance=profile.context)
            if form.is_valid():
                context = form.save()
                #assert False, profile.context.area
                # context not set on user before?
                if not profile.context:
                    profile.context = context
                    profile.save()
        else:
            form = ContextForm(request.POST)
            if form.is_valid():
                # anonymous users cannot save context, so just create a dummy object and leave
                request.session['context'] = form.save(commit=False)

    return redirect_to(request, request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('resources_index'))

from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.core import serializers
from django.db.models.query import QuerySet
from django.utils import simplejson as json

class GeoJSONEncoder(DateTimeAwareJSONEncoder):
    """ simplejson.JSONEncoder extension: handle querysets """
    def default(self, obj):
        if isinstance(obj, QuerySet):
            return {
                    'type': 'FeatureCollection',
                    'features': list(obj)
            }
        if isinstance(obj, Resource):
            location = obj.tags.filter(key='location').values_list('value', flat=True)
            if len(location) > 0:
                lonlat = location[0].partition(':')[2].split(',')
                json = {
                        'type':'Feature',
                        'properties': {
                            'title': obj.name,
                            'url': reverse('openresources_resource', kwargs={'key':obj.shortname}),
                            'tags': {}
                        }
                }
                
                for tag in obj.tags.all():
                    if tag.key in json['properties']['tags']:
                        json['properties']['tags'][tag.key].append(tag.value)
                    else:
                        json['properties']['tags'][tag.key] = [tag.value]
                    
                try:
                    json['geometry'] = {
                            'type': 'Point', 
                            'coordinates': [float(lonlat[0]),float(lonlat[1])]
                        }
                except:
                    # fail silently if something geos wrong with extracting coords
                    pass
                return json
            return None
        return super(GeoJSONEncoder, self).default(obj)
               
def view_json(request, name=None):

    view = get_object_or_404(View, shortname=name)    
    if view.protected and not request.user.is_authenticated():
        return HttpResponse(status=403) # forbidden

    resources = view.get_resources().filter(tags__key='location')
    if not request.user.is_authenticated():
        resources = resources.filter(protected=False)

    str = json.dumps(resources, cls=GeoJSONEncoder, indent=2)
    
    return HttpResponse(str, mimetype='application/json')

def all_json(request):

    try:    
        return view_json(request, 'all')
    except Http404:
        # view with name "all" not found, return all resources without mapping
        pass

    resources = Resource.objects.filter(tags__key='location')
    if not request.user.is_authenticated():
        resources = resources.filter(protected=False)
       
    str = json.dumps(resources, cls=GeoJSONEncoder, indent=2)
    
    return HttpResponse(str, mimetype='application/json')

