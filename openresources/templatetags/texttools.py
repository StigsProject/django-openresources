from django import template
from django.template.defaultfilters import stringfilter

import re

register = template.Library()

@register.filter
@stringfilter
def emailize(value, text='email'):
    return re.sub(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9-]+)\.([a-zA-Z0-9.-]+)', r"""<a href="#" title="\1 at \2" onclick="var m='X@Y'.replace('X','\1').replace('Y','\2.\3');this.href='mailto:'+m;this.innerHTML=m;">email</a>""", value)

@register.filter
def in_list(value, list=''):
    return str(value) in list.split(',')

@register.filter
@stringfilter
def prefix(value, prefix):
    return "%s%s" % (prefix, value)

@register.simple_tag
def smart_date(start_date=None, end_date=None, date_format='j.n.'):
    from datetime import datetime
    from django.utils import dateformat

    now = datetime.now()

    components = []

    if start_date:
        components.append(dateformat.format(start_date, date_format))
        if start_date.year != now.year: components.append(str(start_date.year))
        
        start_time = start_date.time()
        if start_time.hour > 0 or start_time.minute > 0:
            components.append(dateformat.time_format(start_time,r',&\n\b\s\p;G:i'))

    if end_date:
        components.append(' &ndash; ')
        if (not start_date) or end_date.date() != start_date.date():
            components.append(dateformat.format(end_date, date_format))
            if end_date.year != now.year: components.append(str(end_date.year))

        end_time = end_date.time()
        if end_time.hour > 0 or end_time.minute > 0:
            components.append(dateformat.time_format(end_time,r',&\n\b\s\p;G:i'))
    
    return ''.join(components)
    
