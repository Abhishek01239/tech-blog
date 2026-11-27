---
title: "Deploying Hugo on Vercel the Reliable Way: Pin the Version With a Build Script"
date: 2026-11-27T07:55:00+05:30
draft: false
description: "Why Hugo builds on Vercel can break without warning, and how a short build script pins the exact Hugo version, adds a pre-build safety check, and gives you reproducible deployments."
categories: ["DevOps"]
image: "/images/covers/hugo-vercel-pin-version-build-script-v2.jpg"
author: "Jaiswar Abhishek"
---

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

Pinning production is only half the job. While writing this post I checked which Hugo my *local* setup used, and found that the two had drifted far apart.

The repository's `package.json` installs Hugo for local development through the `hugo-bin` npm package:

```json
"devDependencies": {
  "hugo-bin": "^0.130.1"
}
```

Each `hugo-bin` release downloads a specific Hugo version by default, and version 0.130.1 of the package is set to Hugo **0.133.1**. You can check what any release uses without installing it:

```bash
npm view hugo-bin@0.130.1 hugoVersion
# 0.133.1
```

So `npx hugo server` on my laptop was running Hugo 0.133.1, while every deployment used 0.167.0, more than thirty minor releases apart. Anything that changed between those versions could work in production and fail locally, or the other way round, which defeats the point of pinning.

`hugo-bin` lets you choose the Hugo version explicitly in a `hugo-bin` section of `package.json`, so the fix is to put the same number there as in `build.sh`:

```json
"hugo-bin": {
  "version": "0.167.0"
}
```

After changing it, run `npm rebuild hugo-bin` so the new binary is downloaded, then confirm with `npx hugo version`. Now there are two places to update when upgrading, but both sit next to each other in the same pull request, and a mismatch is easy to spot in review. If you want to remove the duplication entirely, `build.sh` can read the version from `package.json` with `node -p "require('./package.json')['hugo-bin'].version"`.

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
