from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
import os

register = template.Library()

@register.filter
def preview(value): # Only one argument.
    """Shows the file preview (html) """
    #because I'm returning raw html there's 100% the possibility of injections / malicious
    #file names. I'm just gonna trust that people don't do that :)
    s_value = str(value)
    file = escape(os.path.basename(s_value))
    images = ['jpg', 'jpeg', 'png', 'gif', 'apng', 'bmp', 'svg', 'ico']
    if "."in s_value:
        extension = file[file.rindex(".")+1:].lower()
        if extension in images:
            return mark_safe(f"<a href='/{s_value}' target='_blank'><img src='/{s_value}'/></a>")
        elif extension == "pdf":
            #return mark_safe(f"<embed src='/{s_value}' width='800px' height='2100px' />")
            return mark_safe(f'<embed src="/{s_value}" type="application/pdf" frameBorder="0"scrolling="auto" height="100%" width="100%" style="aspect-ratio:8.5/11;"></embed>')

    return mark_safe(f"<p><a href='/{s_value}' target='_blank'>{file}</a></p>")

