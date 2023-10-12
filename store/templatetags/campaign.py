from atexit import register
from django import template
from store.models import Campaign

register =template.Library()

@register.filter()
def campaign_menu(request):
    return Campaign.objects.filter()