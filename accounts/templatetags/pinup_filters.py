from django import template
from django.utils.html import format_html
from django.urls import reverse

register = template.Library()

@register.simple_tag
def nav_link(text, url, path, *classes):
    reversed_url = reverse(url)
    if path == reversed_url:
        classes = list(classes)
        classes.append('active')
    html = "<a href='{}' class='" + ' '.join(classes) + "'>{}</a>" if classes else "<a href='{}'>{}</a>"
    return format_html(html, reversed_url, text)

