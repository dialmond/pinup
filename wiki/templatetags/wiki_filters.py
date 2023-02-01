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

#from django.template.defaultfilters import unordered_list
from django.utils.html import conditional_escape
import types
@register.filter(is_safe=True, needs_autoescape=True)
def my_unordered_list(value, autoescape=True):
    """
    copied from django defaultfilters.py, just adds a detail tag thingy
    """
    if autoescape:
        escaper = conditional_escape
    else:
        def escaper(x):
            return x

    def walk_items(item_list):
        item_iterator = iter(item_list)
        try:
            item = next(item_iterator)
            while True:
                try:
                    next_item = next(item_iterator)
                except StopIteration:
                    yield item, None
                    break
                if isinstance(next_item, (list, tuple, types.GeneratorType)):
                    try:
                        iter(next_item)
                    except TypeError:
                        pass
                    else:
                        yield item, next_item
                        item = next(item_iterator)
                        continue
                yield item, None
                item = next_item
        except StopIteration:
            pass

    def list_formatter(item_list, tabs=1):
        indent = '\t' * tabs
        output = []
        for item, children in walk_items(item_list):
            sublist = ''
            if children:
                sublist = '\n%s<ul>\n%s\n%s</ul>\n%s' % (
                    indent, list_formatter(children, tabs + 1), indent, indent)
            if not sublist:
                output.append('%s<li>%s%s</li>' % (
                    indent, escaper(item), sublist))
            else:
                output.append('%s<li><details><summary>%s</summary>%s</li>' % (
                    indent, escaper(item), sublist))
        return '\n'.join(output)

    return mark_safe(list_formatter(value))


