"""Module is a gunicorn wrapper for server_factory.create_app, uwsgi works fine
with app factories but gunicorn needs to have instance of the app, hence
this wrapper.
"""

from . import server_factory

app = server_factory.create_app()
