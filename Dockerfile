# Multi-stage build for the vitrine static site.
#
# Stage 1 (builder): install the package with the [site] extra, run the gate,
# and render the static site to /out.
# Stage 2 (runtime): nginx:alpine serving /out — no Python, no app server.
#
# The site is a pure projection of the curated data/: inline-styled HTML, no
# JS, no external assets. nginx just serves files.
#
# The runtime base image is pinned to an immutable digest for reproducibility.
# To bump: pull the latest manifest-list digest with
#   docker buildx imagetools inspect nginx:alpine --format '{{.manifest.digest}}'
# and replace the digest below, then rebuild and verify.

FROM python:3.13-slim AS builder

WORKDIR /build

COPY pyproject.toml ./
COPY src/ src/
COPY data/ data/

RUN pip install --no-cache-dir ".[site]"

# The gate runs first (vitrine build runs check internally); a red gate
# fails the image build — no unverifiable site ships.
RUN vitrine build --out /out

# nginx:alpine pinned 2026-08-09 — sha256 is the OCI image-index digest
# (covers amd64/arm64/arm/386/ppc64le/riscv64/s390x). See header note to bump.
FROM nginx:alpine@sha256:4a73073bd557c65b759505da037898b61f1be6cbcc3c2c3aeac22d2a470c1752

# Strip the default nginx config that serves /usr/share/nginx/html and
# replace it with a minimal static-file server for /out.
RUN rm /etc/nginx/conf.d/default.conf
COPY deploy/nginx.conf /etc/nginx/conf.d/vitrine.conf

COPY --from=builder /out /out

EXPOSE 8080