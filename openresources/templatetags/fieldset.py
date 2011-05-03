import copy

from django import template
from django import forms
from django.utils.datastructures import SortedDict

register = template.Library()

def fieldset(parser, token):
    try:
        name, fields, as_, variable_name, from_, form = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('bad arguments for %r'  % token.split_contents()[0])

    return FieldSetNode(fields.split(','), variable_name, form)

fieldset = register.tag(fieldset)



class FieldSetNode(template.Node):
    """
    Usage:
    {% fieldset field1,field2,field3 as fields from form %}
    <fieldset>
    {{ personal_fields.as_p }}
    </fieldset>
    """
    def __init__(self, fields, variable_name, form_variable):
        self.fields = fields
        self.variable_name = variable_name
        self.form_variable = form_variable

    def render(self, context):
        
        form = template.Variable(self.form_variable).resolve(context)
        fields = self.fields

        # if it is a modelform, get real fieldnames of translated fields from transmeta
        if hasattr(form, '_meta') and hasattr(form._meta, 'model'):
            try:
                from transmeta import get_all_translatable_fields, get_real_fieldname_in_each_language
                trans_fields = get_all_translatable_fields(form._meta.model)
                for field in trans_fields:
                    if field in fields:
                        fields.remove(field)
                        fields.extend(get_real_fieldname_in_each_language(field))
                print fields
            except ImportError:
                pass       

        new_form = copy.copy(form)
                    
        new_form.fields = SortedDict([(key, value) for key, value in form.fields.items() if key in fields])

        context[self.variable_name] = new_form

        return u''

