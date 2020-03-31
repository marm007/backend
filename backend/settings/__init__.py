import os

if os.environ.get('SETTINGS') == 'prod':
    from .prod import *
else:
    from .dev import *