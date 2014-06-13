"""
WSGI config for pysite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

#import newrelic.agent
#newrelic.agent.initialize('/opt/pysite/newrelic.ini',)

import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pysite.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

path = '/opt/pysite'
if path not in sys.path:
    sys.path.append(path)
