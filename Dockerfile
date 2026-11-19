# Multi-stage build for the vitrine static site.
#
# Stage 1 (builder): install the package with the [site] extra, run the gate,
# and render the static site to /out.
# Stage 2 (runtime): nginx stable-alpine serving /out — no Python, no app server.
#
# The site is a pure projection of the curated data/: inline-styled HTML, no
# JS, no external assets. nginx just serves files.
#
# The runtime base image is pinned to an immutable digest for reproducibility.
# To bump: pull the latest manifest-list digest with
#   docker buildx imagetools inspect nginx:<stable>-alpine --format '{{.manifest.digest}}'
# and replace the digest below, then rebuild and verify.

# python:3.13-slim pinned 2026-11-19 (build-only stage; index digest).
FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90 AS builder

WORKDIR /build

COPY pyproject.toml uv.lock ./
COPY src/ src/
COPY data/ data/

RUN pip install --no-cache-dir uv==0.12.5 \
    && uv sync --locked --no-dev --extra site

# The gate runs first (vitrine build runs check internally); a red gate
# fails the image build — no unverifiable site ships.
RUN .venv/bin/vitrine build --out /out

# nginx stable branch 1.30.7 pinned 2026-11-19 (security audit: the 1.31.x
# mainline was affected by 2026 advisories; stable 1.30.7 is not). sha256 is
# the OCI image-index digest. Stay on the stable branch; see header note to bump.
FROM nginx:1.30.7-alpine@sha256:bef154735288bc38d99fac41ae63730684bcc661503673a04a0f9bc526ba8598

# Strip the default nginx config that serves /usr/share/nginx/html and
# replace it with a minimal static-file server for /out.
RUN rm /etc/nginx/conf.d/default.conf
COPY deploy/nginx.conf /etc/nginx/conf.d/vitrine.conf

COPY --from=builder /out /out

EXPOSE 8080