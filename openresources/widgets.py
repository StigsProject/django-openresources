from django.forms.widgets import Widget, HiddenInput, Select
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.forms.util import flatatt

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


class ComboBox(Select):
    """
    Input widget with additional configurable dropdown of values.
    """
    def __init__(self, attrs=None, choices=[], empty_label=None):
        super(ComboBox, self).__init__(attrs, choices)
        self.empty_label=empty_label

    def render(self, name, value, attrs=None, choices=(), empty_label=''):

        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(value)
        output = [u'<input type="text"%s />' % flatatt(final_attrs)]
        options = self.render_options(choices, [value])
        if options:
            output.append(u'<select class="combo-select" id="%s_SELECT">' % (final_attrs['id']))
            output.append(self.render_option([value], '', self.empty_label or empty_label))
            output.append(options)
            output.append(u'</select>')
        return mark_safe(u'\n'.join(output))

    class Media:
        js = ('openresources/js/edit.js')

