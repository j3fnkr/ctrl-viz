FROM python:3.10-slim
LABEL authors="Jan"

RUN useradd --create-home --shell /bin/bash --uid 1000 ubuntu

WORKDIR /home/app

# setup.py reads README.md at build time
COPY README.md setup.py ./
COPY src/ ./src/

RUN pip install --no-cache-dir ".[web]"

EXPOSE 8050

RUN chown -R ubuntu:ubuntu /home/app
USER ubuntu

# Production behind Caddy (reverse_proxy to this container on port 8050):
#
#   ctrl-viz.example.com {
#       reverse_proxy ctrl-viz:8050
#   }
#
# Caddy sets X-Forwarded-* headers automatically. Gunicorn must trust them:
#   --proxy-headers --forwarded-allow-ips=172.16.0.0/12
# (172.16.0.0/12 covers default Docker bridge networks; restrict further if you prefer)
#
# Do not expose port 8050 publicly when Caddy terminates TLS in front.
CMD ["gunicorn", "ctrl_viz.web.wsgi:server", "--bind", "0.0.0.0:8050", "--workers", "2", "--timeout", "120", "--proxy-headers", "--forwarded-allow-ips=172.16.0.0/12"]
