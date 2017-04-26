# -*- coding: utf-8 -*-

REFRESH = request.is_local or 'refresh' in request.vars
common = local_import('common', reload=REFRESH)

session.connect(request, response, cookie_key='XXX', compression_level=None)


## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

response.generic_patterns = ['*'] if request.is_local else []

from gluon.tools import Auth, Crud, Service, PluginManager, Recaptcha, prettydate
auth = Auth(db)

crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = False
auth.settings.actions_disabled = ['request_reset_password', 'change_password', 'retrieve_password']

places = common.Places(db)
