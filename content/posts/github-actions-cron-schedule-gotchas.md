---
title: "GitHub Actions Cron Schedules: Time Zones, Delays and the 60-Day Shutoff"
date: 2026-11-27T07:45:00+05:30
draft: false
description: "A practical guide to scheduled GitHub Actions workflows from someone who runs a dozen of them: reading cron in UTC and IST, the new timezone field, why runs start late or not at all, the 60-day shutoff, overlapping runs, and how to notice silent failures."
categories: ["DevOps"]
image: "/images/covers/github-actions-cron-schedule-gotchas-v2.jpg"
author: "Jaiswar Abhishek"
---

GitHub Actions is a free scheduler for anyone with a repository. I use it for nearly all of my automation: uploading [Shorts](https://github.com/Abhishek01239/Youtube-Shorts-Automation), cross-posting to Pinterest and Instagram, and refreshing the data behind this site's [Vulnerability Watch](/vuln-watch/). Writing a schedule takes one line of YAML. Making it run when you expect, every day, for months, takes a bit more knowledge.

This guide collects what I've learned from running those workflows, including a real mistake from one of my own files. If you're in India, the time-zone examples will be directly useful, but the rest applies everywhere.

## The basics

A scheduled workflow has a `schedule` trigger with one or more cron expressions:

```yaml
on:
  schedule:
    - cron: "30 4 * * *"
  workflow_dispatch: {}    # adds a manual "Run workflow" button
```

The five fields are minute, hour, day of month, month and day of week. `30 4 * * *` means "at minute 30 of hour 4, every day". Add `workflow_dispatch` to every scheduled workflow; being able to start a run by hand is invaluable for testing.

Four rules from GitHub's documentation catch most people at least once:

- **The default time zone is UTC**, not your time zone and not your runner's.
- **The shortest interval is every 5 minutes.** `* * * * *` won't run every minute.
- **Schedules only run from the default branch.** A schedule in a feature branch does nothing until it's merged.
- **Shortcuts like `@daily` and `@hourly` are not supported.** Write all five fields.

## Reading cron in IST

India Standard Time is UTC+5:30, with no daylight saving time. To convert a UTC schedule to IST, add 5 hours 30 minutes; to go the other way, subtract.

| You want (IST) | UTC | Cron |
|---|---|---|
| 06:00 every day | 00:30 | `30 0 * * *` |
| 09:00 every day | 03:30 | `30 3 * * *` |
| 10:00, 14:00, 18:00 | 04:30, 08:30, 12:30 | `30 4,8,12 * * *` |
| 07:40 on weekdays | 02:10 | `10 2 * * 1-5` |
| 00:15 every day | 18:45 the day before | `45 18 * * *` |

The last row is the one that trips people up: any IST time before 05:30 falls on the *previous* UTC day. If you also restrict the day of the week, shift it by one too.

### A real mistake: the comment and the cron disagree

This is from my own Shorts workflow:

```yaml
schedule:
  # Trigger ONCE daily at 03:30 UTC (09:00 AM IST)
  - cron: '30 0 * * *'
```

The comment says 03:30 UTC. The cron says 00:30 UTC, which is **06:00 IST**, three hours earlier than the comment claims. The schedule had clearly been changed at some point and the comment hadn't. Nothing breaks, so nothing warns you; you only find out when you wonder why uploads happen so early. A comment next to a cron expression is useful, but only if you treat it as part of the code and update both together.

## The `timezone` field

Since March 2026, GitHub Actions accepts an optional IANA time zone next to each cron expression:

```yaml
on:
  schedule:
    - cron: "0 9 * * *"
      timezone: "Asia/Kolkata"    # 09:00 IST
```

This removes the mental arithmetic entirely, and in regions with daylight saving time it also keeps the run at the same local time all year. My Instagram workflow uses it for a long list of posting times, each written directly in IST.

Two cautions. Many tutorials and AI-generated answers still say time zones aren't supported, because the feature is new; trust the [official docs](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule) over older articles. And if your workflow logic compares times (for example, "skip if it's after 22:00"), remember that the runner's clock is still UTC; the `timezone` field only changes when the run is triggered.

## Runs start late, and some never start

GitHub's documentation is direct about this: scheduled runs can be delayed when Actions is under heavy load, the start of every hour is one of those busy moments, and if load is high enough, some queued runs may be dropped. A dropped run doesn't fail. It simply never happens, so there's no red cross to notice.

What helps:

- **Avoid minute 0.** Thousands of workflows are scheduled for `0 * * * *`. Pick an odd minute like `7` or `43`. My Instagram schedule uses minutes such as 7, 36 and 5, which also makes the posts look less mechanical.
- **Don't depend on exact timing.** If something must happen at a precise moment, a scheduled workflow is the wrong tool. Treat "09:00" as "some time after 09:00".
- **Make each run catch up.** Design jobs to process everything that's pending, not just "today's item". My YouTube-to-Pinterest workflow looks at all videos from the last 72 hours and skips ones already posted. If one run is dropped, the next one covers it.

## The 60-day shutoff

In **public** repositories, GitHub automatically disables scheduled workflows when there has been no repository activity for 60 days. Activity means things like commits, pull requests or issues; a workflow running successfully on its own doesn't count.

This catches automation that works perfectly. You set it up, it runs fine for two months, you stop touching the repository, and then it quietly stops. GitHub sends an email warning beforehand, which is easy to miss.

Ways to handle it:

- **Re-enable it when warned.** On the repository's Actions tab, choose the workflow and click **Enable workflow**.
- **Let the workflow create activity.** Workflows that commit their state back to the repository (as my Shorts pipeline does with its upload history) produce regular commits. Be careful with this approach when several jobs push at once; I describe a nasty trap in [Why `git rebase -X ours` Silently Threw Away My Workflow's Commit](/posts/git-rebase-x-ours-github-actions-state/).
- **Use a private repository** if the code doesn't need to be public. The 60-day rule applies to public repositories.

## Overlapping runs

A schedule doesn't check whether the previous run has finished. My ClipPilot worker runs every 15 minutes (`*/15 * * * *`) and can take up to 25. Without protection, two copies would process the same queue at the same time.

The fix is a `concurrency` group:

```yaml
concurrency:
  group: daily-posts
  cancel-in-progress: false
```

With `cancel-in-progress: false`, a new run waits for the current one to finish instead of running alongside it. Use `true` instead when only the newest run matters (for example, a deploy that would be outdated anyway). Combine this with `timeout-minutes` on the job so a stuck run can't block the queue for the default six hours.

## Several schedules in one workflow

You can list multiple cron entries and check which one fired using `github.event.schedule`:

```yaml
on:
  schedule:
    - cron: "30 3 * * *"     # 09:00 IST: daily run
    - cron: "30 3 * * 0"     # 09:00 IST Sundays: weekly report

jobs:
  report:
    if: github.event.schedule == '30 3 * * 0'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Weekly report"
```

The value is the cron string exactly as written, so copy it character for character.

## Noticing silent failures

The hardest problems with scheduled workflows are the ones that produce no error: a dropped run, a disabled schedule, a job that "succeeds" without doing anything. A few habits help:

1. **Send a notification at the end of important runs**, success or failure. My Shorts pipeline can send a Telegram message after each upload. If the message doesn't arrive, I know something is wrong without having to check.
2. **Fail loudly when nothing happened unexpectedly.** If a job that should always find work finds none, exit with an error.
3. **Check the Actions tab weekly** for a gap in the run history, not just for red crosses.
4. **Keep secrets valid.** Many scheduled jobs fail weeks later because an access token expired. Note the expiry date of every token you add as a secret.

## A template to start from

```yaml
name: Daily job

on:
  schedule:
    - cron: "17 3 * * *"          # 08:47 IST; odd minute avoids the busy top of the hour
  workflow_dispatch: {}

concurrency:
  group: daily-job
  cancel-in-progress: false

permissions:
  contents: read                 # widen only if the job must push

jobs:
  run:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: python job.py
        env:
          API_KEY: ${{ secrets.API_KEY }}
```

It runs at an unusual minute, can be started by hand, never overlaps itself, can't run forever, and starts with read-only permissions. That covers most of the problems in this guide before they happen.

## Sources

- [GitHub Docs: events that trigger workflows, `schedule`](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule) (UTC default, timezone field, 5-minute minimum, default branch, delays, 60-day rule)
- [GitHub Changelog: GitHub Actions late March 2026 updates](https://github.blog/changelog/2026-03-19-github-actions-late-march-2026-updates/) (time zone support for schedules)
- [GitHub Docs: control the concurrency of workflows and jobs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)
- [GitHub Docs: disabling and enabling a workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows)
