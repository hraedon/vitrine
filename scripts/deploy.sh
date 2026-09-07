#!/usr/bin/env bash
# Deploy the museum's exact current-main image, then prove the live site
# actually changed.
#
# The cluster is not reachable from GitHub-hosted runners. CI publishes both a
# convenience :main tag and a commit tag; this script refuses dirty or stale
# checkouts and selects the commit tag so another build cannot race a rollout.
#
# The verification step is the point. `kubectl rollout status` reports that new
# pods are running, which is not the same claim as "visitors see the current
# corpus" — the pods could have pulled a stale layer, or the build could have
# failed upstream leaving the old image at :main. Comparing the served pages, assets, and exports
# against a local build detects content and UI changes even when IDs stay the same.
#
# Usage: scripts/deploy.sh --context CONTEXT [--namespace vitrine] [--url URL]

set -euo pipefail

NAMESPACE="vitrine"
DEPLOYMENT="vitrine"
URL="https://vitrine.hraedon.com"
CONTEXT=""
IMAGE="ghcr.io/hraedon/vitrine"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VITRINE="$REPO_ROOT/.venv/bin/vitrine"
PYTHON="$REPO_ROOT/.venv/bin/python"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --namespace) NAMESPACE="$2"; shift 2 ;;
        --url) URL="$2"; shift 2 ;;
        --context) CONTEXT="$2"; shift 2 ;;
        -h|--help) sed -n '2,20p' "${BASH_SOURCE[0]}"; exit 0 ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

cd "$REPO_ROOT"

if [[ -z "$CONTEXT" ]]; then
    echo "--context is required; choose the intended kubectl context explicitly" >&2
    exit 2
fi

if [[ -n "$(git status --porcelain)" ]]; then
    echo "refusing to deploy a dirty checkout" >&2
    exit 2
fi

git fetch --quiet origin main
REVISION="$(git rev-parse HEAD)"
if [[ "$REVISION" != "$(git rev-parse origin/main)" ]]; then
    echo "refusing to deploy: HEAD is not origin/main" >&2
    exit 2
fi
IMAGE_TAG="sha-${REVISION:0:7}"

if [[ ! -x "$VITRINE" || ! -x "$PYTHON" ]]; then
    echo "Vitrine's project environment is missing; run: uv venv && uv pip install -e '.[dev]'" >&2
    exit 2
fi

echo "==> Building the current corpus to compare against"
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT
"$VITRINE" build --out "$BUILD_DIR/site" >/dev/null
echo "    built $(wc -l < "$BUILD_DIR/site/facts-manifest.txt") fact(s)"

echo "==> Deploying tested image $IMAGE:$IMAGE_TAG"
kubectl --context "$CONTEXT" set image "deployment/$DEPLOYMENT" \
    "vitrine=$IMAGE:$IMAGE_TAG" -n "$NAMESPACE"
kubectl --context "$CONTEXT" rollout status \
    "deployment/$DEPLOYMENT" -n "$NAMESPACE" --timeout=5m

DEPLOYED_IMAGE="$(kubectl --context "$CONTEXT" get "deployment/$DEPLOYMENT" \
    -n "$NAMESPACE" -o jsonpath='{.spec.template.spec.containers[?(@.name=="vitrine")].image}')"
if [[ "$DEPLOYED_IMAGE" != "$IMAGE:$IMAGE_TAG" ]]; then
    echo "rollout selected $DEPLOYED_IMAGE, expected $IMAGE:$IMAGE_TAG" >&2
    exit 1
fi

# New pods answer readiness before the CDN/ingress necessarily routes to them.
echo "==> Waiting for the live site to settle"
sleep 10

echo "==> Verifying the live site serves the current corpus"
if "$PYTHON" scripts/check_deploy_freshness.py \
    "$BUILD_DIR/site" --url "$URL"; then
    echo
    echo "Deployed. $URL now serves the current corpus."
else
    status=$?
    echo
    echo "Rollout completed but verification FAILED (exit $status)." >&2
    echo "The pods restarted; the site does not match the corpus." >&2
    echo "Check that CI published the image for the current main commit:" >&2
    echo "  gh run list -R hraedon/vitrine --workflow ci.yml --limit 3" >&2
    exit "$status"
fi
