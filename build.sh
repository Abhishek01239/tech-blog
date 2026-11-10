#!/usr/bin/env bash
set -euo pipefail

HUGO_VERSION="0.167.0"
HUGO_CACHEDIR="${PWD}/.vercel/cache/hugo"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT SIGINT SIGTERM

export HUGO_CACHEDIR

echo "Installing Hugo ${HUGO_VERSION}..."
curl -sfL --output "${TMP_DIR}/hugo.tar.gz" "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_${HUGO_VERSION}_linux-amd64.tar.gz"
mkdir -p "${HOME}/.local/hugo"
tar -C "${HOME}/.local/hugo" -xf "${TMP_DIR}/hugo.tar.gz"
export PATH="${HOME}/.local/hugo:${PATH}"

echo "Using: $(hugo version)"
echo "Checking editorial approval state..."
for post in content/posts/*.md; do
  [ -f "$post" ] || continue
  if grep -Eq "^review_status:[[:space:]]*['\"]?needs-review['\"]?[[:space:]]*$" "$post" \
    && grep -Eq "^draft:[[:space:]]*false[[:space:]]*$" "$post"; then
    echo "ERROR: $post is marked needs-review but is not a draft."
    echo "Complete the editorial review, then set draft: false and review_status: approved."
    exit 1
  fi
done

echo "Building TechPulse..."
hugo build --gc --minify
