

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


from django import forms
from django.forms import Form, ModelForm
from django.forms.fields import IntegerField, BooleanField
from django.forms.models import inlineformset_factory, BaseInlineFormSet, BaseModelFormSet, ModelChoiceField, InlineForeignKeyField
from django.forms.widgets import Widget, HiddenInput
from django.forms.formsets import BaseFormSet, TOTAL_FORM_COUNT, DELETION_FIELD_NAME, ORDERING_FIELD_NAME
from django.utils.translation import string_concat, ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.forms.util import flatatt
from django.db import connections

from openresources.models import *

# commenting out AutoCompleteWidget usage for now, probably needs custom widget to do what we need
#from autocomplete.widgets import AutoCompleteWidget

#class JQueryACWidget(AutoCompleteWidget):
#    """
#    This widget uses JQuery served from MEDIA_URL.
#    """
#    class Media:
#        extend = False
#        css = {'all': ('js/thickbox.css',)}
#        js = ('js/jquery.min.js',
#            'js/jquery.bigframe.min.js',
#            'js/jquery.ajaxQueue.js',
#            'js/thickbox-compressed.js',
#            'js/jquery.autocomplete.min.js',
#            'js/jquery_autocomplete.js')

class ResourceForm(ModelForm):
    
    def __init__(self, user, *args, **kwargs):
        super(ResourceForm, self).__init__(*args, **kwargs)
        
        #if not user.has_perm('resources.feature_resource'):
        #    del self.fields['featured']
        
    #key = forms.CharField(widget=AutoCompleteWidget('keys', force_selection=False))
    
    class Meta:
        model = Resource
        exclude = ('creator','featured','start_date','end_date')


def tagformcallback(field):
# autocomplete won't return distinct values, so disable for now
#    if field.name == 'key':
#        return forms.CharField(widget=AutoCompleteWidget('keys', force_selection=False))
    return field.formfield()

_TagFormSet = inlineformset_factory(Resource, Tag,
                                   exclude=('creator',),
                                   extra=1,
                                   fk_name='resource',
                                   formfield_callback=tagformcallback)

class TagFormSet(_TagFormSet):
        
    def __init__(self, user, *args, **kwargs):
        if not user.has_perm('openresources.delete_tag'):
            self.can_delete = False
        super(TagFormSet, self).__init__(*args, **kwargs)


class IconForm(ModelForm):

    class Meta:
        model = Icon
        exclude = ('creator')
        

class ViewForm(ModelForm):
    
    def __init__(self, user, *args, **kwargs):
        super(ViewForm, self).__init__(*args, **kwargs)
        
        if not user.has_perm('openresources.feature_view'):
            del self.fields['featured']

    #key = forms.CharField(widget=AutoCompleteWidget('keys', force_selection=False))
    
    class Meta:
        model = View
        exclude = ('creator','sub_views','order_by')


QueryFormSet = inlineformset_factory(View, TagQuery,
                                   exclude=('creator',),
                                   extra=1)


TagMappingFormSet = inlineformset_factory(View, TagMapping,
                                   exclude=('creator',),
                                   extra=1)


class ContextForm(ModelForm):

    area = forms.ModelChoiceField(queryset=Area.objects.all(), required=False, empty_label=_('Everywhere'), label=_('Area'))
    
    class Meta:
        model = Context


class ResourceTemplateForm(ModelForm):

    class Meta:
        model = ResourceTemplate
        exclude = ('creator',)

TagTemplateFormSet = inlineformset_factory(TagTemplateGroup, TagTemplate,
                                   exclude=('creator',),
                                   extra=1)


class ConstWidget(Widget):
    """
    Non-editable Widget that only displays its value.
    """
    def __init__(self, label=None, *args, **kwargs):
        self.label=label
        super(ConstWidget, self).__init__(*args, **kwargs)

    def _format_value(self, value):
        if self.is_localized:
            return formats.localize_input(value)
        return value

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        final_attrs['value'] = force_unicode(self._format_value(value))
        final_attrs['type'] = 'hidden'
        return mark_safe(u'%s <code>[%s]</code><input%s />' % (self.label, value, flatatt(final_attrs)))


class TemplateTagForm(ModelForm):

    value = forms.CharField(required=False, widget=forms.Textarea())

    def __init__(self, template=None, *args, **kwargs):
        self.template = template
        super(TemplateTagForm, self).__init__(*args, **kwargs)
        if self.template:
            self.fields['key'] = forms.CharField(widget=ConstWidget(label=template.name), initial=template.key)
            #self.fields['value'].widget=forms.Textarea()

    class Meta:
        model = Tag
        exclude=('creator',)

    def as_tr(self):
        "Returns this form rendered as <td>s in a single table row - without the <tr> tags."
        return self._html_output(
            normal_row = u'<td>%(errors)s%(field)s%(help_text)s</td>',
            error_row = u'<td>%s</td>',
            row_ender = u'</td>',
            help_text_html = u'<br />%s',
            errors_on_separate_row = False)
        

class BaseTemplateFormSet(BaseInlineFormSet):
    """
    A customized FormSet for rendering a resource's tags according to a Template.
    """
    def __init__(self, template, *args, **kwargs):

        # initial data and can_order is not supported
        if kwargs.get('initial'):
            raise ValueError('TemplateFormSet does not support initial values.')
        if kwargs.get('can_order'):
            raise ValueError('TemplateFormSet does not support ordering.')

        self.template = template
        self.templates = template.tags.all()
        self.can_delete = kwargs.pop('can_delete', False)

        super(BaseTemplateFormSet, self).__init__(*args, **kwargs)

    def get_tags_by_key(self, key):
        if not hasattr(self, '_tag_dict'):
            self._tag_dict = {None:[]}
            for tag in self.get_queryset():
                for template in self.templates:
                    if tag.key == template.key:
                        if not tag.key in self._tag_dict:
                            self._tag_dict[tag.key] = []
                        self._tag_dict[tag.key].append(tag)
                        break
                else:
                    self._tag_dict[None].append(tag)                
                
        return self._tag_dict.get(key)

    def _construct_forms(self):

        self.forms = []
        i = 0

        for template in self.templates:
            tags = self.get_tags_by_key(template.key)
            if not tags or len(tags)==0:
                # create empty form
                self.forms.append(self._construct_form(i, template=template))
                i += 1
            else:
                for tag in tags:
                    self.forms.append(self._construct_form(i, template=template, instance=tag))
                    i += 1
        tags = self.get_tags_by_key(None)
        if tags:
            for tag in tags:
                self.forms.append(self._construct_form(i, instance=tag))
                i += 1

        for i in xrange(i, i+self.extra):
            self.forms.append(self._construct_form(i))


    def _construct_form(self, i, **kwargs):

        defaults = {'auto_id': self.auto_id, 'prefix': self.add_prefix(i), 'empty_permitted' : True}
    
        if self.is_bound and kwargs.get('instance'):
            pk_key = "%s-%s" % (self.add_prefix(i), self.model._meta.pk.name)
            pk = self.data[pk_key]
            pk_field = self.model._meta.pk
            pk = pk_field.get_db_prep_lookup('exact', pk,
                connection=connections[self.get_queryset().db])
            if isinstance(pk, list):
                pk = pk[0]
            kwargs['instance'] = self._existing_object(pk)

        if self.data or self.files:
            defaults['data'] = self.data
            defaults['files'] = self.files

        defaults.update(kwargs)
        form = self.form(**defaults)
        if kwargs.get('template'):
            form._group = kwargs['template'].group
        self.add_fields(form, kwargs.get('instance'))

        if self.save_as_new:
            # Remove the primary key from the form's data, we are only
            # creating new instances
            form.data[form.add_prefix(self._pk_field.name)] = None

            # Remove the foreign key from the form's data
            form.data[form.add_prefix(self.fk.name)] = None

        # Set the fk value here so that the form can do it's validation.
        setattr(form.instance, self.fk.get_attname(), self.instance.pk)
        return form

    def add_fields(self, form, instance):
# from BaseModelFormset:
        """Add a hidden field for the object's primary key."""
        from django.db.models import AutoField, OneToOneField, ForeignKey
        self._pk_field = pk = self.model._meta.pk
        # If a pk isn't editable, then it won't be on the form, so we need to
        # add it here. 
        def pk_is_not_editable(pk):
            return ((not pk.editable) or (pk.auto_created or isinstance(pk, AutoField))
                or (pk.rel and pk.rel.parent_link and pk_is_not_editable(pk.rel.to._meta.pk)))
        if pk_is_not_editable(pk) or pk.name not in form.fields:
            if form.is_bound:
                pk_value = form.instance.pk
            else:
                if instance:
                    pk_value = instance.pk
                else:
                    pk_value = None
            if isinstance(pk, OneToOneField) or isinstance(pk, ForeignKey):
                qs = pk.rel.to._default_manager.get_query_set()
            else:
                qs = self.model._default_manager.get_query_set()
            qs = qs.using(form.instance._state.db)
            form.fields[self._pk_field.name] = ModelChoiceField(qs, initial=pk_value, required=False, widget=HiddenInput)

# oderdering currently not supported
#        if self.can_order:
#            # Only pre-fill the ordering field for initial forms.
#            if index is not None and index < self.initial_form_count():
#                form.fields[ORDERING_FIELD_NAME] = IntegerField(label=_(u'Order'), initial=index+1, required=False)
#            else:
#                form.fields[ORDERING_FIELD_NAME] = IntegerField(label=_(u'Order'), required=False)
        if self.can_delete:
            form.fields[DELETION_FIELD_NAME] = BooleanField(label=_(u'Delete'), required=False)

# from BaseInlineFormset:
        if self._pk_field == self.fk:
            name = self._pk_field.name
            kwargs = {'pk_field': True}
        else:
            # The foreign key field might not be on the form, so we poke at the
            # Model field to get the label, since we need that for error messages.
            name = self.fk.name
            kwargs = {
                'label': getattr(form.fields.get(name), 'label', capfirst(self.fk.verbose_name))
            }
            if self.fk.rel.field_name != self.fk.rel.to._meta.pk.name:
                kwargs['to_field'] = self.fk.rel.field_name

        form.fields[name] = InlineForeignKeyField(self.instance, **kwargs)

        # Add the generated field to form._meta.fields if it's defined to make
        # sure validation isn't skipped on that field.
        if form._meta.fields:
            if isinstance(form._meta.fields, tuple):
                form._meta.fields = list(form._meta.fields)
            form._meta.fields.append(self.fk.name)

    def total_form_count(self):
        """Returns the total number of forms in this FormSet."""
        if self.data or self.files:
            return self.management_form.cleaned_data[TOTAL_FORM_COUNT]
        else:
            initial_forms = self.template.tags.count()
            total_forms = initial_forms + self.extra

        return total_forms

    def as_table(self):
        "Returns this formset rendered as HTML <tr>s -- excluding the <table></table>."
        html = []    
        group = None
        for form in self.forms:
            cur_group = getattr(form,'_group',None)
            if cur_group != group:
                if group:
                    html.append('</tbody>')              
                html.append(string_concat('<tbody><tr><th>', cur_group and cur_group.name or _('More Tags'), '</th></tr><tr>'))
                group = cur_group
            else:
                html.append('<tr>')
            html.append(form.as_tr())
            html.append('</tr>')
        return mark_safe(string_concat(unicode(self.management_form), *html))

TemplateFormSet = inlineformset_factory(Resource, Tag, formset=BaseTemplateFormSet, form=TemplateTagForm, extra=1, fk_name='resource')





