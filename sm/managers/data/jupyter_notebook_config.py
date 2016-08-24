# See http://ipython.org/ipython-doc/1/interactive/public_server.html for more information.
# Configuration file for ipython-notebook.
import os

c = get_config()
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.port = 8888
c.NotebookApp.open_browser = False
c.NotebookApp.profile = u'default'
c.IPKernelApp.matplotlib = 'inline'

headers = {
    'X-Frame-Options': 'ALLOWALL',
}
c.NotebookApp.allow_origin = '*'
c.NotebookApp.allow_credentials = True

c.NotebookApp.base_url = '/ipython/'
c.NotebookApp.webapp_settings = {'static_url_prefix':'/ipython/static/'}

if os.environ.get('NOTEBOOK_PASSWORD', 'none') != 'none':
    c.NotebookApp.password = os.environ['NOTEBOOK_PASSWORD']

if os.environ.get('CORS_ORIGIN', 'none') != 'none':
    c.NotebookApp.allow_origin = os.environ['CORS_ORIGIN']

c.NotebookApp.webapp_settings['headers'] = headers