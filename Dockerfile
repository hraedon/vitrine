# Multi-stage build for the vitrine static site.
#
# Stage 1 (builder): install the package with the [site] extra, run the gate,
# and render the static site to /out.
# Stage 2 (runtime): nginx:alpine serving /out — no Python, no app server.
#
# The site is a pure projection of the curated data/: inline-styled HTML, no
# JS, no external assets. nginx just serves files.

FROM python:3.13-slim AS builder

WORKDIR /build

COPY pyproject.toml ./
COPY src/ src/
COPY data/ data/

RUN pip install --no-cache-dir ".[site]"

# The gate runs first (vitrine build runs check internally); a red gate
# fails the image build — no unverifiable site ships.
RUN vitrine build --out /out

FROM nginx:alpine

# Strip the default nginx config that serves /usr/share/nginx/html and
# replace it with a minimal static-file server for /out.
RUN rm /etc/nginx/conf.d/default.conf
COPY deploy/nginx.conf /etc/nginx/conf.d/vitrine.conf

COPY --from=builder /out /out

EXPOSE 8080