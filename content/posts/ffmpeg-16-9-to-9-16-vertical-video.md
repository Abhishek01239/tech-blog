---
title: "Turning 16:9 Footage Into 9:16 Shorts With FFmpeg: Crop, Blur-Fill and Split Layouts"
date: 2026-11-27T07:35:00+05:30
draft: false
description: "Three tested FFmpeg filter graphs that convert landscape video into 1080×1920 vertical video for Shorts, Reels and TikTok: centre crop, blurred-background fill, and a facecam split layout, with the trade-offs of each."
categories: ["Automation"]
image: "/images/covers/ffmpeg-16-9-to-9-16-vertical-video.jpg"
author: "Jaiswar Abhishek"
---

Gameplay, screen recordings and most camera footage are landscape (16:9). Shorts, Reels and TikTok want portrait (9:16). Converting between them sounds like one setting, but it is really a design decision: a vertical frame is less than a third as wide as a landscape frame of the same height, so something has to give.

My [Shorts automation pipeline](https://github.com/Abhishek01239/Youtube-Shorts-Automation) supports three layouts and chooses between them per video. This post gives each one as a plain FFmpeg command, explains every filter, and shows what the output actually looks like. I ran every command below with FFmpeg 6.1 on a generated test clip, so you can copy them as they are.

## Setting up a test clip

You don't need real footage to experiment. FFmpeg can generate a 1920×1080 test pattern with a tone:

```bash
ffmpeg -f lavfi -i testsrc2=size=1920x1080:rate=30 \
       -f lavfi -i "sine=frequency=440:sample_rate=48000" \
       -t 8 -c:v libx264 -c:a aac -shortest in.mp4
```

Test patterns are useful precisely because they are boring: the coloured bars make it obvious which part of the original frame survives each layout.

![Three vertical frames side by side: a centre crop showing only two colour bars, a blur-fill showing the full frame in the middle over a blurred background, and a split layout with a cropped region on top and the cropped frame below.](/images/posts/ffmpeg-vertical-layouts.png)

*The three layouts produced by the commands below, from the same 1920×1080 test clip.*

## Layout 1: centre crop

```bash
ffmpeg -i in.mp4 \
  -vf "scale=-1:1920:flags=lanczos,crop=1080:1920:(in_w-1080)/2:0,setsar=1" \
  -c:a copy crop.mp4
```

What each filter does:

- **`scale=-1:1920`** scales the video to 1920 pixels tall. The `-1` means "work out the width to keep the aspect ratio", giving about 3413 pixels wide.
- **`flags=lanczos`** chooses the Lanczos scaling algorithm, which keeps more detail than the default when enlarging.
- **`crop=1080:1920:(in_w-1080)/2:0`** cuts out a 1080×1920 window. The x position `(in_w-1080)/2` centres it horizontally; y is 0.
- **`setsar=1`** sets square pixels so players don't stretch the result.

**Trade-off:** the output fills the screen and looks native, but it keeps only 1080 of the 3413 scaled pixels, about 32% of the original width. In the image above, only two of the eight colour bars survive. For gameplay that means the minimap, health bar, kill feed and anything happening off-centre are cut away. Centre crop works well when the action really is in the middle: a single person talking, a centred game character.

## Layout 2: blurred-background fill

This is the layout you've probably seen most: the whole landscape frame in the middle, with a blurred, zoomed copy of itself filling the space above and below.

```bash
ffmpeg -i in.mp4 -filter_complex "
  [0:v]split[a][b];
  [a]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,
     boxblur=luma_radius=12:luma_power=2,
     eq=brightness=-0.10:saturation=1.15,
     scale=1080:1920:flags=bicubic[bg];
  [b]scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos[fg];
  [bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[v]
" -map "[v]" -map 0:a -c:a copy blur.mp4
```

This needs `-filter_complex` because one input becomes two streams that are processed differently and then combined.

- **`split[a][b]`** duplicates the video into two streams.
- **Background (`[a]`)**: scale to fill a 270×480 frame (`force_original_aspect_ratio=increase` enlarges until both sides are covered), crop off the excess, blur it, darken it slightly and boost saturation, then scale it up to 1080×1920.
- **Foreground (`[b]`)**: scale the full frame to *fit inside* 1080×1920 (`force_original_aspect_ratio=decrease`), which makes it 1080×608.
- **`overlay=(W-w)/2:(H-h)/2`** centres the foreground on the background. `W`/`H` are the background's size and `w`/`h` the foreground's.

**Why blur at 270×480?** Blurring is expensive, and its cost grows with the number of pixels. Blurring a quarter-size frame and scaling it up is far cheaper than blurring a full 1080×1920 frame, and because the result is supposed to be blurry anyway, nobody can see the difference. The darkening (`brightness=-0.10`) keeps the background from competing with the real picture.

**Trade-off:** nothing is cut off, which makes this the safest default for gameplay. The cost is size: the actual content occupies only 608 of the 1920 pixels of height, under a third of the screen. On a phone, small on-screen text becomes hard to read.

## Layout 3: split screen with a facecam

Streamers usually have a webcam overlay in a corner. A split layout puts that face in a panel at the top and the gameplay below, which suits vertical screens because both halves are large.

```bash
ffmpeg -i in.mp4 -filter_complex "
  [0:v]split[f][g];
  [f]crop=480:270:1440:810,scale=1080:640:flags=lanczos,setsar=1[face];
  [g]scale=1080:1280:force_original_aspect_ratio=increase:flags=lanczos,
     crop=1080:1280,setsar=1[game];
  [face][game]vstack=inputs=2[v]
" -map "[v]" -map 0:a -c:a copy split.mp4
```

- **`crop=480:270:1440:810`** cuts the facecam region out of the source: 480×270 pixels starting at x=1440, y=810 (the bottom-right corner in this example). This box must match where the webcam actually is.
- The face panel is scaled to **1080×640**, and the gameplay is scaled and cropped to **1080×1280**. 640 + 1280 = 1920, so the two panels exactly fill the frame.
- **`vstack=inputs=2`** stacks the two streams vertically. Both must have the same width, which is why each branch ends at exactly 1080 pixels wide.

The hard part isn't FFmpeg, it's knowing where the facecam is. Every streamer puts theirs somewhere different. My pipeline samples about ten frames with OpenCV's Haar-cascade face detector, looks for a small face that stays in roughly the same place across the clip, and builds the crop box from that. If it can't find a stable face, it falls back to the blur layout. A face that moves around is probably part of the game, not a webcam.

**Trade-off:** the most engaging layout when it works, and the most fragile. A wrong crop box produces a panel of random scenery at the top of the video.

## Choosing automatically

In the pipeline, the default `framing` setting is `"auto"`: split if a facecam is detected, otherwise blur. Crop is available per channel for content where the action is reliably centred. Beyond that, the pipeline lets a [multi-armed bandit](/posts/thompson-sampling-bandit-video-editing/) test the layouts against each other and learn which one keeps viewers watching longest.

## Details that make a difference

**Use the same width everywhere.** `vstack` and `overlay` fail or misalign if branch sizes don't match exactly. Ending every branch with an explicit size (and `setsar=1`) avoids most "Input link parameters do not match" errors.

**Speed changes need two filters.** My pipeline plays Shorts at 1.2× speed. Video speed uses `setpts=0.833333*PTS` (1 / 1.2 ≈ 0.8333), and audio needs its own `atempo=1.2`, which changes speed without changing pitch. Forgetting the audio filter leaves the sound out of sync.

**Encode once at high quality.** If several processing steps each write an MP4, quality drops with every re-encode. The pipeline writes intermediate files at CRF 15 (nearly lossless) and does the final, smaller encode only at the end, together with loudness normalisation, which I cover in [Two-Pass Loudness Normalisation With FFmpeg loudnorm](/posts/ffmpeg-loudnorm-two-pass-14-lufs/).

**Check the length rules you are building for.** My code still caps clips at 45 seconds, a habit from when Shorts had a 60-second limit. Since 15 October 2024, YouTube counts square or vertical uploads of up to three minutes as Shorts. Shorter is often still better for retention, but it should be a choice, not an outdated limit.

## Python, if you prefer

The pipeline itself builds these graphs with the `ffmpeg-python` library, which writes the same filter graph from Python code. The blur layout looks like this:

```python
parts = video.filter_multi_output("split")
bg = (parts[0]
      .filter("scale", 270, 480, force_original_aspect_ratio="increase")
      .filter("crop", 270, 480)
      .filter("boxblur", luma_radius=12, luma_power=2)
      .filter("eq", brightness=-0.10, saturation=1.15)
      .filter("scale", 1080, 1920, flags="bicubic"))
fg = parts[1].filter("scale", 1080, 1920, force_original_aspect_ratio="decrease", flags="lanczos")
v = ffmpeg.overlay(bg, fg, x="(W-w)/2", y="(H-h)/2").filter("setsar", 1)
```

It's convenient once a pipeline grows, but I'd recommend getting each layout working as a plain command first. When something breaks, a command you can paste into a terminal is much easier to debug.

## Sources

- [FFmpeg filters documentation](https://ffmpeg.org/ffmpeg-filters.html): `scale`, `crop`, `boxblur`, `overlay`, `vstack`, `setpts`, `atempo`
- [FFmpeg wiki: scaling](https://trac.ffmpeg.org/wiki/Scaling)
- [YouTube Help: understand three-minute YouTube Shorts](https://support.google.com/youtube/answer/15424877)
- [OpenCV: cascade classifier tutorial](https://docs.opencv.org/4.x/db/d28/tutorial_cascade_classifier.html)
- Source code: [video_processor.py](https://github.com/Abhishek01239/Youtube-Shorts-Automation/blob/main/video_processor.py)
