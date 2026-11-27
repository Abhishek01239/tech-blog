---
title: "A Bandit That Edits Videos: Thompson Sampling in Practice"
date: 2026-11-27T07:30:00+05:30
draft: false
description: "How my YouTube Shorts pipeline uses a multi-armed bandit with Thompson sampling to learn which editing choices keep viewers watching: the reward formula, the Beta-distribution code, a simulation of how fast it learns, and its real limits."
categories: ["Automation"]
image: "/images/covers/thompson-sampling-bandit-video-editing-v2.jpg"
author: "Jaiswar Abhishek"
---

My [YouTube Shorts automation](https://github.com/Abhishek01239/Youtube-Shorts-Automation) turns gaming clips into vertical Shorts on a schedule. Every Short involves small editing decisions: blur the background or crop the frame, add zoom "punch-ins" or not, which font to use for the headline, whether to cut a 20-second or a 40-second moment.

I could guess the best settings and hard-code them. Instead, the pipeline treats each decision as an experiment and learns from how the published Shorts actually perform. The technique is called a **multi-armed bandit**, and the version it uses, **Thompson sampling**, fits in about 250 lines of Python with no machine-learning libraries.

This post explains how it works, using the real code, and then uses a simulation to answer the question I care most about: how long does it take to learn anything?

## The problem a bandit solves

Imagine a row of slot machines (in old slang, "one-armed bandits"), each paying out at a different, unknown rate. You have a limited number of coins. Every coin spent on a bad machine is wasted, but if you only play the machine that looks best right now, you might never discover a better one.

That's the **explore–exploit trade-off**, and it describes many real choices: which headline to show, which thumbnail to test, which editing style to use. A bandit algorithm decides, one round at a time, which option to try next, balancing learning (explore) against using what it already knows (exploit).

A bandit is the simplest form of reinforcement learning. There's no long chain of actions and no changing environment state to model, just: choose, observe a reward, update.

## What the pipeline chooses

The bandit picks one option in each of six dimensions for every Short:

```python
DIMENSIONS = {
    "framing": ["auto", "blur", "crop"],
    "punch_ins": ["on", "off"],
    "headline_font": ["luckiest", "anton", "bangers", "bebas"],
    "caption_font": ["luckiest", "anton", "bangers", "bebas"],
    "clip_length": ["short", "medium", "long"],
    "moment_style": ["balanced", "audio", "speech", "action"],
}
```

`clip_length` maps to 15–25, 25–35 or 35–45 seconds. `moment_style` changes how the moment finder weighs loudness, on-screen motion and speech when it looks for the best part of a clip. The framing options are the three FFmpeg layouts I describe in [Turning 16:9 Footage Into 9:16 Shorts With FFmpeg](/posts/ffmpeg-16-9-to-9-16-vertical-video/).

## The reward: turning analytics into one number

A bandit needs a single number per round, between 0 and 1. Each Short is scored once it has been public for at least 72 hours (and no more than 28 days):

```python
def compute_reward(m, median_views):
    views = max(0, m.get("views", 0))
    views_rel = views / (views + max(1.0, median_views))          # 0.5 = median
    if m.get("source") == "analytics" and views > 0:
        # 25% watched -> 0, 100% -> 1
        retention = min(1.0, max(0.0, (m.get("avg_view_pct", 0.0) - 25.0) / 75.0))
        subs_rel = min(1.0, (m.get("subs", 0) / views * 1000) / 5.0)
        return 0.60 * retention + 0.25 * views_rel + 0.15 * subs_rel
    like_rel = min(1.0, (m.get("likes", 0) / views) / 0.06) if views else 0.0
    return 0.70 * views_rel + 0.30 * like_rel
```

Three design choices are worth explaining:

- **Retention gets the most weight (60%).** How much of a Short people watch depends directly on the edit. Raw view counts depend heavily on things the edit can't control, such as which clip was available that day and how the algorithm distributed it.
- **Views are compared with the channel's median,** using `v / (v + median)`. A Short with exactly median views scores 0.5, double the median scores 0.67, and the value can never exceed 1. One viral video can't swamp everything else.
- **There's a fallback.** Retention requires the YouTube Analytics API and an extra OAuth permission. Without it, the reward uses public views and the like rate, which is noisier but better than nothing.

## Thompson sampling in a few lines

Each option keeps a **Beta distribution**, described by two numbers `a` and `b`. You can read them loosely as "successes plus one" and "failures plus one". Every option starts at `a = 1, b = 1`, a flat distribution meaning "anything between 0 and 1 is equally likely".

To choose, the code draws one random sample from each option's distribution and takes the highest:

```python
draws = {opt: rng.betavariate(arms[opt]["a"], arms[opt]["b"]) for opt in opts}
choices[dim] = max(draws, key=draws.get)
```

That's the whole policy. Its elegance is in what the distributions do over time:

- An option with **little data** has a wide distribution, so it sometimes produces a high sample and gets tried. That's exploration, and it happens automatically.
- An option with **lots of good results** has a narrow distribution near a high value, so it wins most draws. That's exploitation.
- An option with **lots of bad results** narrows near a low value and stops winning, without ever being banned outright.

On top of that, 10% of choices are fully random (`explore = 0.1`), as a safety net so no option is ever completely abandoned.

### Updating with a fractional reward

The textbook version of Thompson sampling uses rewards that are exactly 0 or 1 (a click or no click). This pipeline's rewards are fractions like 0.63, so it adds the reward to `a` and the remainder to `b`:

```python
opts[opt]["a"] += reward
opts[opt]["b"] += 1.0 - reward
```

A Short with reward 0.63 counts as 0.63 of a success and 0.37 of a failure. This is a common, practical extension. It keeps the mean of each distribution, `a / (a + b)`, equal to the average reward the option has earned.

### Forgetting slowly

Before every update, all options decay slightly towards their starting point:

```python
DECAY = 0.995
arm["a"] = 1.0 + (arm["a"] - 1.0) * DECAY
arm["b"] = 1.0 + (arm["b"] - 1.0) * DECAY
```

Without this, evidence from a year ago would count as much as last week's. Audience taste and YouTube's recommendation system both change, so old results should matter less. A decay of 0.995 per update means a result's weight halves after about 140 further updates, and the bandit effectively remembers the last couple of hundred Shorts.

## How fast does it learn? A simulation

All of that sounds sensible, but the practical question is speed. A channel posts a handful of Shorts a day at most. How many does the bandit need before it reliably favours the better option?

I wrote a small simulation using exactly the update rules above, for one dimension with three options. I gave them hidden "true" average rewards of 0.58, 0.50 and 0.42, a realistic gap, and added random noise to each reward (standard deviation 0.15) because real performance varies a lot from video to video. Then I ran 300 simulated channels for 180 Shorts each:

```python
for _ in range(n_videos):
    if rng.random() < EXPLORE:
        choice = rng.choice(OPTIONS)
    else:
        draws = {o: rng.betavariate(arms[o]["a"], arms[o]["b"]) for o in OPTIONS}
        choice = max(draws, key=draws.get)
    reward = min(1.0, max(0.0, rng.gauss(TRUE_MEAN[choice], 0.15)))
    # ...decay all arms, then add reward to the chosen arm...
```

![Line chart: share of simulated channels choosing each clip length over 180 Shorts. The best option rises from about 31% to about 65%; the worst falls to about 12%.](/images/posts/bandit-convergence-v2.png)

Here's how often the best option ("short") was chosen, averaged over the 300 runs:

| Shorts | Best option chosen | Worst option chosen |
|---|---|---|
| 1–10 | 38% | 29% |
| 51–60 | 54% | 17% |
| 171–180 | 65% | 12% |

Three things stand out.

**It learns, but slowly.** After 60 Shorts, about two months at one a day, the best option is picked only a little over half the time. That's not a flaw in Thompson sampling; it's what noisy rewards with small gaps look like. When the difference between options is eight points and the noise is fifteen, you need many observations to be confident.

**It levels off around 65%.** Two things cap it. The 10% random exploration always spends some Shorts on other options. And because the decay keeps forgetting old evidence, the distributions never become very narrow, so the second-best option still wins a fair number of draws. That's the price of being able to adapt when tastes change.

**It reliably avoids the worst option.** The clearest gain early on is that the weakest choice is abandoned. Even if a bandit takes months to find the very best setting, cutting the obviously bad ones quickly is valuable.

## Limits worth knowing

Building this taught me as much about what a bandit *can't* do as what it can:

- **Each dimension is learned separately.** One Short's reward is credited to all six of its choices at once. That assumes the choices don't interact. In reality, a headline font might work well only with a particular layout. A bandit that modelled combinations would need far more data, because there are 3 × 2 × 4 × 4 × 3 × 4 = 1,152 of them.
- **Rewards arrive late.** Each Short is scored only after 72 hours, so the bandit always acts on information that's at least three days old. That's unavoidable when the signal is audience behaviour.
- **The reward is a choice, not a fact.** Weighting retention at 60% is my decision about what "good" means. If the weights are wrong, the bandit will learn efficiently towards the wrong goal.
- **Noise from outside the edit is huge.** Which clip was picked, the time of day and the topic all affect performance more than the font. The bandit treats all of that as noise, which is one more reason it needs many Shorts.

## Making it survive GitHub Actions

The pipeline runs on GitHub Actions, where every run starts on a fresh machine with no memory of the last one. The bandit keeps its state in two JSON files per channel, `rl_state.json` (the `a` and `b` values) and `rl_log.json` (which options each Short used). The workflow commits both back to the repository after each run. Writes go to a temporary file first and are then renamed into place, so a crash can't leave a half-written file:

```python
def _write_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)
```

Committing state from parallel jobs has its own trap. I wrote about the one I found in [Why `git rebase -X ours` Silently Threw Away My Workflow's Commit](/posts/git-rebase-x-ours-github-actions-state/).

Everything is also designed to fail open: if the state file can't be read, the pipeline uses the channel's normal settings and keeps publishing. A learning system should never be the reason a scheduled upload doesn't happen.

## Should you use a bandit?

If you're making repeated choices, can measure an outcome for each one, and have enough rounds, a bandit is a simple and honest way to let data decide instead of guessing. Thompson sampling is a good default: few settings to tune, and exploration that fades naturally as evidence builds up.

Just be realistic about the numbers. With noisy outcomes and small differences, it takes many rounds to learn. Run a quick simulation with your own expected volume before you build, so you know whether you'll see results in a week or in six months.

## Sources

- Russo, Van Roy, Kazerouni, Osband and Wen, [*A Tutorial on Thompson Sampling*](https://arxiv.org/abs/1707.02038) (2018)
- Agrawal and Goyal, [*Analysis of Thompson Sampling for the Multi-armed Bandit Problem*](https://arxiv.org/abs/1111.1797), which covers rewards between 0 and 1
- [Python documentation: `random.betavariate`](https://docs.python.org/3/library/random.html#random.betavariate)
- [YouTube Analytics API: metrics](https://developers.google.com/youtube/analytics/metrics) (`averageViewPercentage`, `subscribersGained`)
- Source code: [rl/bandit.py and rl/update_rewards.py](https://github.com/Abhishek01239/Youtube-Shorts-Automation/tree/main/rl)
