"""Production WSGI entry point for Gunicorn.

Served by Gunicorn; put Caddy in front for TLS, e.g.::

    ctrl-viz.example.com {
        reverse_proxy ctrl-viz:8050
    }

Use ``--proxy-headers`` and ``--forwarded-allow-ips`` in Gunicorn so Flask/Dash
see the correct client IP and scheme (see Dockerfile CMD).
"""

from ctrl_viz.web.app import create_app

app = create_app()
server = app.server
