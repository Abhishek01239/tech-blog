---
title: "Why git rebase -X ours Silently Threw Away My Workflow's Commit"
date: 2026-11-27T07:50:00+05:30
draft: false
description: "During a rebase, 'ours' means the branch you are rebasing onto, not your own changes. A reproducible demo of how `git rebase -X ours` drops a GitHub Actions job's state commit without any error, and safer ways to push state from parallel jobs."
categories: ["DevOps"]
image: "/images/covers/git-rebase-x-ours-github-actions-state-v2.jpg"
author: "Jaiswar Abhishek"
---

Several of my GitHub Actions workflows save state by committing files back to the repository: which videos have been uploaded, what the [editing bandit](/posts/thompson-sampling-bandit-video-editing/) has learned, and so on. When several jobs run in parallel, they race to push, and the losers have to fetch the new commits and try again.

The retry step in my Shorts workflow looks reasonable at first glance:

```bash
git commit -m "auto: update ${CHANNEL} history [skip ci]"
git fetch origin main
git rebase -X ours origin/main || git rebase --abort || true
git push origin main
```

The intent is clear: "if there's a conflict, keep *our* version." The problem is that during a rebase, Git's idea of "ours" is the opposite of what most people expect. This post shows, with a script you can run, exactly what that line does, and what to use instead.

## "Ours" and "theirs" flip during a rebase

In a **merge**, "ours" is the branch you're on and "theirs" is the branch you're merging in. That matches intuition.

A **rebase** works differently. Git checks out the branch you're rebasing *onto* (here, `origin/main`) and then replays your commits on top of it, one by one. While it does that, the branch being built is the upstream one. So:

- **`ours`** = the upstream branch you're rebasing onto (`origin/main`, the *other* job's work)
- **`theirs`** = your own commits being replayed

Git's documentation says this explicitly in the `git rebase` manual: with `-X ours` and `-X theirs`, the sides are swapped compared to a merge. It's documented, but very easy to miss.

So `git rebase -X ours origin/main` means: **"when there's a conflict, prefer the remote's version and discard mine."**

## Reproducing it

Here's a self-contained script that simulates two workflow jobs updating the same state file. It uses a local bare repository as the "remote", so it's safe to run anywhere:

```bash
set -e
G="git -c init.defaultBranch=main -c user.email=x@x -c user.name=x"

$G init -q --bare origin.git
$G clone -q origin.git a; cd a
echo '{"seen": []}' > state.json
$G add .; $G commit -qm init; $G push -q origin main

# Job B starts from the same commit, records video-B and pushes first
cd ..; $G clone -q origin.git b; cd b
echo '{"seen": ["video-B"]}' > state.json
$G commit -qam "job B: saw video-B"; $G push -q origin main

# Job A records video-A, but its push is rejected
cd ../a
echo '{"seen": ["video-A"]}' > state.json
$G commit -qam "job A: saw video-A"
$G push -q origin main || echo "push rejected (job B got there first)"

# The retry logic from the workflow
$G fetch -q origin main
$G rebase -X ours origin/main && echo "rebase -X ours: succeeded, no conflict reported"
echo "state.json now: $(cat state.json)"
$G log --oneline
```

Output:

```
push rejected (job B got there first)
rebase -X ours: succeeded, no conflict reported
state.json now: {"seen": ["video-B"]}
249c73f job B: saw video-B
9c141a1 init
```

Read that carefully. The rebase **succeeded**. There was no conflict message. And job A's commit **no longer exists**: the log shows only `init` and job B's commit. Job A's change conflicted, `-X ours` resolved the conflict in favour of the remote, which left job A's commit with no changes at all, and Git drops commits that become empty during a rebase. The following `git push` then has nothing new to push and succeeds too.

From the workflow's point of view, everything went green. In reality, job A's record that it uploaded `video-A` was thrown away, so a later run could upload the same video again.

## Does this actually happen in my workflow?

It depends on which files collide, and it's worth being precise. In my Shorts workflow, each parallel matrix job handles one channel and only writes that channel's files (`data/channels/<channel>/...`). Jobs for *different* channels change different files, so their rebases don't conflict and both sets of changes survive. That's why this bug stayed invisible.

The danger is two runs of the **same** channel overlapping, for example a manual "Run workflow" started while the scheduled run is still going. Both edit the same `upload_log.json` and `rl_log.json`, and the second one to push loses its updates silently.

## Safer patterns

There are several better options, from simplest to most robust.

### 1. Don't let the same state be written twice at once

Prevent the overlap in the first place with a concurrency group per channel:

```yaml
concurrency:
  group: shorts-${{ matrix.channel }}
  cancel-in-progress: false
```

Runs for the same channel now queue instead of overlapping, while different channels still run in parallel. For my workflow this removes the dangerous case entirely, and it's a two-line change.

### 2. Let conflicts fail

If you remove `-X ours`, a real conflict stops the rebase with an error. Failing is better than silently losing data: the run goes red, and you find out. Combined with a retry loop, it also handles the common case, because a rebase with no conflict succeeds normally.

```bash
for i in 1 2 3 4 5; do
  git fetch origin main
  if ! git rebase origin/main; then
    git rebase --abort
    echo "Real conflict in state files; refusing to overwrite." >&2
    exit 1
  fi
  git push origin main && exit 0
  sleep $((i * 5))
done
exit 1
```

### 3. Merge the data, not the text

The deeper problem is that Git merges files line by line, but a JSON log or a list of seen IDs has meaning Git doesn't understand. Two jobs adding different entries to the same list is not a real conflict at all; the right answer is both entries.

So on conflict, rebuild the file from both versions in code. For an append-only list of IDs:

```bash
git fetch origin main
git show origin/main:data/seen_videos.txt > /tmp/remote.txt
sort -u /tmp/remote.txt data/seen_videos.txt -o data/seen_videos.txt
git reset --soft origin/main     # move onto the remote, keep our working files
git add data/seen_videos.txt
git commit -m "auto: merge history [skip ci]"
git push origin main
```

`sort -u` combines both lists and removes duplicates, so nothing is lost no matter who pushed first. JSON files can be merged the same way with a few lines of Python. One caution with this pattern: `git reset --soft` makes your next commit contain *every* difference between your files and the remote, so it's only safe when your job changes nothing except the files you merge.

### 4. Keep state somewhere designed for it

Committing to Git is convenient for small projects, and it gives you history for free. But a repository isn't a database. Once several jobs write the same state frequently, a small hosted database (I use Supabase for another project) or even one file per run (`runs/2026-11-27-channelA.json`, which never conflicts) is a better fit.

## The general lesson

`-X ours` and `-X theirs` are blunt tools: they resolve every conflicting part of every file in one direction, without telling you. In scripts that run unattended, that silence is the problem. Prefer approaches that either avoid conflicts (concurrency groups, separate files) or resolve them with knowledge of the data (merging lists), and let anything else fail loudly.

And if you only remember one thing: **in a rebase, "ours" is the branch you're rebasing onto.**

## Sources

- [Git documentation: git-rebase](https://git-scm.com/docs/git-rebase) (note on how "ours" and "theirs" are swapped during a rebase, and the `-X` strategy options)
- [Git documentation: merge strategies, the `ours` option of the `ort` strategy](https://git-scm.com/docs/merge-strategies)
- [GitHub Docs: control the concurrency of workflows and jobs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)
- Workflow discussed: [upload_short.yml](https://github.com/Abhishek01239/Youtube-Shorts-Automation/blob/main/.github/workflows/upload_short.yml)
