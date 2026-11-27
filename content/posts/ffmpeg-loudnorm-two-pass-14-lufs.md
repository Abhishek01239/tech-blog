---
title: "Two-Pass Loudness Normalisation With FFmpeg loudnorm"
date: 2026-11-27T07:40:00+05:30
draft: false
description: "How to make every video play at a consistent loudness with FFmpeg's loudnorm filter: what LUFS and true peak mean, a tested two-pass script in Python, and why loudnorm can silently fall back to dynamic mode."
categories: ["Automation"]
image: "/images/covers/ffmpeg-loudnorm-two-pass-14-lufs-v2.jpg"
author: "Jaiswar Abhishek"
---

If you publish videos from many different sources, their volume will be all over the place. One gaming clip is whisper-quiet, the next one is a streamer screaming into a cheap microphone. Viewers notice immediately, and the usual reaction to a sudden loud video is to swipe away.

My [Shorts automation pipeline](https://github.com/Abhishek01239/Youtube-Shorts-Automation) fixes this with a final "mastering" step that normalises every video to the same loudness using FFmpeg's `loudnorm` filter. This post explains the measurements involved, gives a working two-pass script, and shows one surprising behaviour I found while testing it. Every number below is real output from FFmpeg 6.1.

## Loudness is not the same as volume

The obvious approach is to make the loudest sample in each file hit the maximum level (peak normalisation). It doesn't work well, because the loudest instant of a file tells you little about how loud it *sounds*. A clip with one gunshot and quiet talking can peak at maximum and still sound quiet overall.

**Loudness normalisation** measures perceived loudness across the whole file instead, using the method in ITU-R BS.1770 and the EBU R128 recommendation. Three measurements matter:

- **Integrated loudness**, in **LUFS** (Loudness Units relative to Full Scale): the average perceived loudness of the whole programme. Higher (closer to 0) is louder. A change of 1 LU is the same size as 1 dB.
- **True peak**, in **dBTP**: the highest level the waveform actually reaches, including peaks that fall *between* digital samples once the audio is converted back to analogue. Keeping it below 0 prevents clipping, and lossy encoders like AAC can raise peaks slightly, so a margin is wise.
- **Loudness range (LRA)**, in LU: how much the loudness varies between quiet and loud passages.

## Choosing the targets

My pipeline uses these values:

```python
TARGET_LUFS = -14.0
TARGET_TP = -1.5
TARGET_LRA = 11.0
```

**-14 LUFS** is the figure most often quoted for YouTube and several music streaming services. YouTube doesn't publish an official target, but it does turn down videos that are louder than its reference level, so mastering much louder than about -14 gains nothing and costs dynamics. **-1.5 dBTP** leaves headroom for the AAC encoder. **LRA 11** is permissive enough that speech and game sound keep their natural ups and downs.

## Why two passes?

`loudnorm` can run in one pass. It then has to adjust the gain *as it goes*, without knowing what comes later, which is called dynamic mode. It works, but it acts like an automatic volume control and can audibly pump on content with big jumps.

With two passes you measure the whole file first, then give those measurements to the second pass. If the file allows it, the second pass applies **one constant gain** to the entire file (linear mode), which sounds exactly like the original, just louder or quieter.

## Pass 1: measure

```bash
ffmpeg -hide_banner -nostats -i input.mp4 -vn \
  -af "highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json" \
  -f null -
```

`-vn` skips the video and `-f null -` throws away the output: we only want the measurements, which `loudnorm` prints as JSON at the end of its log. For a 20-second test file of pink noise with a slowly varying level, I got:

```json
{
	"input_i" : "-27.87",
	"input_tp" : "-17.65",
	"input_lra" : "1.20",
	"input_thresh" : "-37.87",
	"output_i" : "-14.05",
	"output_tp" : "-3.97",
	"output_lra" : "1.10",
	"output_thresh" : "-24.05",
	"normalization_type" : "dynamic",
	"target_offset" : "0.05"
}
```

The `input_*` values are the ones you need. Ignore `normalization_type` here: pass 1 has no measurements to work from, so it always reports dynamic.

The `highpass=f=70` in front removes rumble below 70 Hz (microphone handling noise, desk bumps). That energy is hard to hear but still affects the measurement, so removing it first gives a more honest loudness figure.

## Pass 2: apply

Feed the measurements back in with `measured_*` options, plus `linear=true`:

```bash
ffmpeg -i input.mp4 -c:v copy \
  -af "highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=-27.87:measured_TP=-17.65:measured_LRA=1.20:measured_thresh=-37.87:offset=0.05:linear=true:print_format=json,aresample=48000" \
  -c:a aac -b:a 192k output.mp4
```

The second pass reported `"normalization_type" : "linear"`, and measuring the result with FFmpeg's `ebur128` filter confirmed it:

```
input.mp4    integrated -27.6 LUFS, true peak -15.1 dBTP
output.mp4   integrated -13.9 LUFS, true peak  -3.8 dBTP
```

Within 0.1 LU of the target, with plenty of peak headroom.

The final `aresample=48000` matters. `loudnorm` works internally at 192 kHz for accurate true-peak detection, and without resampling you can end up with a 192 kHz output, which wastes space and which some platforms handle badly.

## The surprise: linear mode isn't guaranteed

I first tested with a perfectly steady 440 Hz tone. Pass 1 measured it at -49.78 LUFS with an LRA of exactly 0.00. I passed those numbers into pass 2 with `linear=true`, and pass 2 reported:

```
"normalization_type" : "dynamic"
```

No error and no warning; the filter quietly used dynamic mode instead. Linear mode is only used when it can actually work. It requires, for example, that the constant gain needed to reach the target wouldn't push the true peak over your limit. Here that condition was met (the peak would have landed around -8.7 dBTP), so something else ruled it out. The likely cause is visible in the filter's own help text (`ffmpeg -h filter=loudnorm`): the default value of `measured_LRA` is 0. A real measurement of exactly 0 looks identical to "not provided", so the filter acts as if it lacked measurements. Real speech and game audio never have an LRA of exactly zero, which is why the noise test above went linear.

The more common fallback in practice is the peak condition: a quiet recording with one very loud moment needs so much gain that the peak would exceed -1.5 dBTP, so `loudnorm` has to compress dynamically.

The practical lesson: **don't assume pass 2 was linear. Read the `normalization_type` it prints.** Log it, and if most of your files fall back to dynamic, revisit your true-peak target or add a limiter before `loudnorm`.

## The Python version

Here is the core of what my pipeline does, simplified slightly:

```python
import json, re, subprocess

TARGET = "I=-14:TP=-1.5:LRA=11"

def measure(path):
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn",
           "-af", f"highpass=f=70,loudnorm={TARGET}:print_format=json",
           "-f", "null", "-"]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    match = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", res.stderr, re.S)
    if not match:
        return None
    stats = json.loads(match.group(0))
    # Silent clips measure -inf; normalising them would just amplify noise.
    if "inf" in str(stats.get("input_i")):
        return None
    return stats

def audio_filter(stats):
    af = f"highpass=f=70,loudnorm={TARGET}"
    if stats:
        af += (f":measured_I={stats['input_i']}:measured_TP={stats['input_tp']}"
               f":measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}"
               f":offset={stats['target_offset']}:linear=true")
    return af + ",aresample=48000"
```

Three details are deliberate:

- **The JSON is found with a regex** on FFmpeg's log output (`stderr`), because `loudnorm` prints it alongside all the other log lines. The pattern looks for the block containing `"input_i"`.
- **Silent clips are skipped.** A silent file measures `-inf` LUFS. Trying to bring it to -14 would amplify background hiss enormously, so the measurement is treated as missing and pass 2 runs in plain dynamic mode.
- **Failure never blocks publishing.** In the full pipeline, if any FFmpeg step fails, the mastering function returns the original file and the upload goes ahead. A video that is a little quiet is better than no video.

## Quick reference

| Goal | Setting |
|---|---|
| Measure only | `loudnorm=...:print_format=json`, `-vn -f null -` |
| Typical online video target | `I=-14:TP=-1.5:LRA=11` |
| Broadcast (EBU R128) | `I=-23:TP=-1` (the filter's defaults are I=-24, TP=-2, LRA=7) |
| Constant-gain second pass | `measured_*` values + `offset` + `linear=true` |
| Avoid a 192 kHz output | add `aresample=48000` after `loudnorm` |
| Verify the result | `-af ebur128=peak=true -f null -` |

## Sources

- [FFmpeg filters documentation: loudnorm and ebur128](https://ffmpeg.org/ffmpeg-filters.html#loudnorm)
- [EBU R 128: loudness normalisation and permitted maximum level of audio signals](https://tech.ebu.ch/publications/r128)
- [ITU-R BS.1770: algorithms to measure audio programme loudness and true-peak audio level](https://www.itu.int/rec/R-REC-BS.1770)
- Source code: [quality_enhancer.py](https://github.com/Abhishek01239/Youtube-Shorts-Automation/blob/main/quality_enhancer.py)
