"""
 exactly the same as from django.template.defaulttags.url EXCEPT kwargs equal to None are removed
 this allows a bit more flexibility than the use of {% url %} where nesting is rested on optional 
 base kw arguments.
 
 see http://code.djangoproject.com/ticket/9176     
"""

from django import template
from django.template import TemplateSyntaxError
from django.template.defaulttags import URLNode, url

register = template.Library()

class URLNodeOptional(URLNode):    
    """
    identical to django.template.defaulttags.URLNode
    but removes kwargs equal to None before resolving the url
    """
    
    def render(self, context):
        for k, v in self.kwargs.items():
            if v.resolve(context) is None or v.resolve(context) == '':            
                self.kwargs.pop(k)
        return super(URLNodeOptional, self).render(context)

def url_optional(parser, token):    
    """
     creates the default URLNode, then routes it to the Optional resolver with the same properties
     by first creating the URLNode, the parsing stays in django core where it belongs.     
    """ 
    
    urlnode = url(parser, token)
    return URLNodeOptional(urlnode.view_name, urlnode.args, urlnode.kwargs, urlnode.asvar)
    

url_optional = register.tag(url_optional)


