#!/usr/bin/env bash
# Deploy the museum: roll the Deployment onto the current :main image, then
# prove the live site actually changed.
#
# Why a restart is needed at all: k8s/deployment.yaml references the mutable
# tag ghcr.io/hraedon/vitrine:main with imagePullPolicy: Always. That policy
# applies when a pod is *created* — running pods never re-pull. So a fresh
# image in ghcr does not reach visitors until something replaces the pods, and
# nothing in CI does (the cluster is not reachable from GitHub-hosted runners).
# This script is that something.
#
# The verification step is the point. `kubectl rollout status` reports that new
# pods are running, which is not the same claim as "visitors see the current
# corpus" — the pods could have pulled a stale layer, or the build could have
# failed upstream leaving the old image at :main. Comparing the served pages, assets, and exports
# against a local build detects content and UI changes even when IDs stay the same.
#
# Usage: scripts/deploy.sh [--namespace vitrine] [--url https://vitrine.hraedon.com]

set -euo pipefail

NAMESPACE="vitrine"
DEPLOYMENT="vitrine"
URL="https://vitrine.hraedon.com"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --namespace) NAMESPACE="$2"; shift 2 ;;
        --url) URL="$2"; shift 2 ;;
        -h|--help) sed -n '2,20p' "${BASH_SOURCE[0]}"; exit 0 ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

cd "$REPO_ROOT"

echo "==> Building the current corpus to compare against"
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT
uv run vitrine build --out "$BUILD_DIR/site" >/dev/null
echo "    built $(wc -l < "$BUILD_DIR/site/facts-manifest.txt") fact(s)"

echo "==> Restarting deployment/$DEPLOYMENT in namespace $NAMESPACE"
kubectl rollout restart "deployment/$DEPLOYMENT" -n "$NAMESPACE"
kubectl rollout status "deployment/$DEPLOYMENT" -n "$NAMESPACE" --timeout=5m

# New pods answer readiness before the CDN/ingress necessarily routes to them.
echo "==> Waiting for the live site to settle"
sleep 10

echo "==> Verifying the live site serves the current corpus"
if uv run python scripts/check_deploy_freshness.py \
    "$BUILD_DIR/site" --url "$URL"; then
    echo
    echo "Deployed. $URL now serves the current corpus."
else
    status=$?
    echo
    echo "Rollout completed but verification FAILED (exit $status)." >&2
    echo "The pods restarted; the site does not match the corpus." >&2
    echo "Check that Build and Push succeeded for the current main commit:" >&2
    echo "  gh run list -R hraedon/vitrine --workflow build.yaml --limit 3" >&2
    exit "$status"
fi
