---
title: "Deploying Hugo on Vercel the Reliable Way: Pin the Version With a Build Script"
date: 2026-11-15
draft: true
review_status: needs-review
description: "Why Hugo builds on Vercel can break without warning, and how a short build script pins the exact Hugo version, adds a pre-build safety check, and gives you reproducible deployments."
categories: ["Infrastructure"]
author: "Abhishek Jaiswar"
---

<!-- OWNER REVIEW CHECKLIST (delete this comment before publishing)
This describes the real build.sh and vercel.json in your repo.
1. Add the story of why you set it up this way. Did a build break? What did the error look like?
2. Add a screenshot of a Vercel build log showing "Using: hugo v…".
3. Run the steps once more yourself to confirm they still work as described.
4. Then set draft: false and review_status: approved.
-->

This site is built with [Hugo](https://gohugo.io/) and hosted on [Vercel](https://vercel.com/). Every push to the main branch triggers a new build and deployment. That setup is fast and free for a small site, but it has one weak spot: **which version of Hugo does the build actually use?**

If you leave that to the platform, an update you never asked for can change how your templates render, or fail the build entirely. This guide shows the small build script I use to pin Hugo to an exact version, plus a pre-build check that stops unfinished articles from going live by accident.

## Why the Hugo version matters

Hugo moves quickly and regularly deprecates and removes template functions and configuration options. For example, the old `paginate` setting was replaced by a `[pagination]` section, and some older template functions were removed after a deprecation period. A theme that builds perfectly on one version can print warnings or fail outright on a newer one.

On your own laptop you control the version. On a hosting platform you often don't, unless you pin it. A build that silently starts using a different version is hard to debug, because nothing in your repository changed.

## The approach: install Hugo yourself during the build

Instead of relying on whatever Hugo the platform provides, the build downloads an exact release from Hugo's GitHub releases page, puts it on the `PATH`, and uses that. Vercel lets you override the build command in `vercel.json`:

```json
{
  "framework": "hugo",
  "installCommand": "",
  "buildCommand": "chmod a+x build.sh && ./build.sh",
  "outputDirectory": "public"
}
```

- `installCommand` is set to an empty string so Vercel skips its default dependency install step. Nothing is needed from npm in production.
- `buildCommand` runs the script below.
- `outputDirectory` tells Vercel to serve the `public/` folder that Hugo generates.

## The build script

Here is the core of `build.sh`:

```bash
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
curl -sfL --output "${TMP_DIR}/hugo.tar.gz" \
  "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_${HUGO_VERSION}_linux-amd64.tar.gz"
mkdir -p "${HOME}/.local/hugo"
tar -C "${HOME}/.local/hugo" -xf "${TMP_DIR}/hugo.tar.gz"
export PATH="${HOME}/.local/hugo:${PATH}"

echo "Using: $(hugo version)"
hugo build --gc --minify
```

What each part does:

- **`set -euo pipefail`** makes the script stop on the first error, on any unset variable, and on a failure anywhere in a pipeline. Without it, a failed download could carry on and produce a confusing error later.
- **`HUGO_VERSION`** is the single place where the version is set. Upgrading Hugo becomes a one-line, reviewable change in Git.
- **`curl -sfL`**: `-f` makes curl fail on HTTP errors instead of saving an error page as the "tarball", and `-L` follows GitHub's redirect to the download server.
- **`trap cleanup`** deletes the temporary download whether the build succeeds or fails.
- **`HUGO_CACHEDIR`** points Hugo's cache inside `.vercel/cache`, which Vercel keeps between builds, so processed resources don't have to be regenerated every time.
- **`echo "Using: $(hugo version)"`** prints the exact version in the build log, so you can confirm at a glance which Hugo produced a deployment.
- **`--gc --minify`** removes unused cached files and minifies the HTML output.

<!-- OWNER: screenshot of the Vercel build log line "Using: hugo v0.167.0 ..." here. -->

## Adding a pre-build safety check

Pinning the version protects against platform changes. The second risk is human: publishing something that isn't ready. My articles carry a `review_status` field in their front matter. The build script refuses to deploy if any article is still marked `needs-review` but has been set to publish:

```bash
for post in content/posts/*.md; do
  [ -f "$post" ] || continue
  if grep -Eq "^review_status:[[:space:]]*['\"]?needs-review['\"]?[[:space:]]*$" "$post" \
    && grep -Eq "^draft:[[:space:]]*false[[:space:]]*$" "$post"; then
    echo "ERROR: $post is marked needs-review but is not a draft."
    exit 1
  fi
done
```

Because the script runs with `set -e` and exits with code 1, Vercel marks the deployment as failed and the live site stays on the previous version. A check like this costs nothing and turns a policy ("review before publishing") into something the build enforces automatically.

## Keeping local and production in sync

To make sure you test with the same Hugo as production, check your local version against the one in `build.sh`:

```bash
hugo version
```

If you install Hugo through npm with the `hugo-bin` package, you can pin it in `package.json` as well. Just remember to update both places when you upgrade.

## Upgrading safely

When a new Hugo release comes out:

1. Read the [release notes](https://github.com/gohugoio/hugo/releases), especially the sections on deprecations and breaking changes.
2. Change `HUGO_VERSION` in `build.sh` on a separate branch.
3. Push the branch. Vercel builds a **preview deployment** for it without touching the live site.
4. Check the preview and the build log for warnings, then merge.

This takes a couple of minutes and means a Hugo upgrade never surprises you in production.

## Sources

- [Hugo — Host on Vercel](https://gohugo.io/host-and-deploy/host-on-vercel/)
- [Vercel — Project configuration (vercel.json)](https://vercel.com/docs/project-configuration)
- [Hugo — Releases on GitHub](https://github.com/gohugoio/hugo/releases)
- [GNU Bash manual — The set builtin](https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html)
