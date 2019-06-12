"""
WSGI config for doll_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
import django.core.handlers.wsgi

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doll_site.settings')

application = get_wsgi_application()

_application = django.core.handlers.wsgi.WSGIHandler()

DOMAIN_NAME = 'www.lolizhan.net'
def application(environ, start_response):
  if environ['HTTP_HOST'] != DOMAIN_NAME:
    location = DOMAIN_NAME + environ['PATH_INFO']
    if environ.get('QUERY_STRING'):
      location += '?' + environ['QUERY_STRING']
    start_response('301 Redirect', [('Location', location),])
    return []
  return _application(environ, start_response)