from django import template

from asf_rm.settings import VERSION, BUILD, DEBUG
from core.utils import COUNTRY_FLAGS, LANGUAGES

register = template.Library()

@register.simple_tag()
def mira_version():
    return VERSION

@register.simple_tag()
def mira_build():
    return f'{BUILD} (dev)' if DEBUG else BUILD

@register.filter('class')
def _class(obj):
    return obj.__class__.__name__ if obj else ''

@register.filter
def index(List, i):
    return List[int(i)]

@register.filter
def entry_num_array(List):
    return range(len(List))

@register.filter('country_flag')
def country_flag(country_code):
    return COUNTRY_FLAGS.get(country_code, '🌐')

@register.filter('language_name')
def country_name(country_code):
    return LANGUAGES.get(country_code, 'Unknown')