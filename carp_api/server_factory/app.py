"""Module is a gunicorn wrapper for server_factory.create_app, uwsgi works fine
with app factories but gunicorn needs to have instance of the app, hence
this wrapper.
"""

from . import server_factory

app = None


if __name__ == '__main__':
    """Set app only if executed not imported.
    """
    app = server_factory.create_app()
