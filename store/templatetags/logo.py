from django import template
from store.models import WebsiteLogo

register = template.Library()

@register.filter
def logo(request):
    return WebsiteLogo.objects.filter().order_by('-id')[:1]