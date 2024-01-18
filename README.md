# Autolight

Automatically make compilation highlight videos

## Usage

Create a CSV file as below named file.txt. Then run `python -m autolight [auto]generate file.txt`.
If you don't include the `auto`, then the timestamps of the TXT file will be strictly adhered to.
If you do include auto, then autolight will algorithmically adjust timestamps to make a nice movie.


#### Without auto

**file.txt**

```
# these two audio clips will occur one after the other, but start with a silence
audio, media/audio1.mp3, start 0, end 3, volume 0
audio, media/audio1.mp3, start 0, end 10, fadein 1, fadeout 1
audio, media/audio2.mp3, start 9, end 30, fadein .1, fadeout 5

# this video will be muted
video, media/hockey.mp4, start 0, end 2, fadein 1, volume 0

# the text will occur on top of the video (important that text comes after video)
video, media/lacy.mp4, start 0, end 10, volume 0, fadein 1, fadeout 1.2, text, hello world, color red, fontsize 40, duration 10, position center, fadein 5

video, media/hockey.mp4, start 100, end 120, fadein 1, fadeout .2

image, media/photo.png, duration 5, fadein 1, position center, text, goodbye, duration 5, fadeout 5, position center, color purple, fontsize 50

```


#### With auto

- The `majorticks` and `minorticks` entry for the audio gives the timestamps of good transition points. You can tap the timestamps out with `python -m autolight autoticks`. The first entry of either tick list denotes an offset, and the rest of the entries denotes timestamps. If you've done well to accurately record the timestamps, then the offset should be set to `0`. On the other hand, if your timestamps are shifted by `x` seconds, then the offset should be set to `x`. For example, if each timestamp is 0.2 seconds early, then `x=0.2`. If each timestamp is 0.2 seconds late, then `x=-0.2`. `majorticks` denote good transition points. `minorticks` denote less good, but still okay transition points. You can supply both, one, or neither.
- The `trim` option can be `none`, `start`, `end`, or `symmetric` (default if no trim provided). If it is `none`, then the video will be minimally trimmed. Otherwise it will be trimmed from the start, end, or symmetrically on both the start and end.

**file.txt**

```
# these two audio clips will occur one after the other
audio; media/audio1.mp3; fadein 5; majorticks [0, 1.8, 3.2600000000000002, 4.79, 6.32, 7.81, 9.309999999999999, 10.77, 12.219999999999999, 13.77, 15.27, 16.740000000000002, 18.26, 19.790000000000003, 21.200000000000003, 22.77, 24.25, 25.73, 27.19, 28.66, 30.14, 31.67, 33.26, 34.71, 36.24, 37.730000000000004, 39.24, 40.72, 42.26, 43.79, 45.26, 46.77, 48.24, 49.76, 51.25, 52.75, 54.25, 55.75, 57.24, 58.76, 60.27, 61.78, 63.24, 64.72, 66.18, 67.66, 69.24, 70.73, 72.25, 73.73, 75.24, 76.72, 78.23, 79.72, 81.2, 82.73, 84.26, 85.74, 87.27, 88.76, 90.26, 91.77, 93.27, 94.75, 96.25, 97.81, 99.25, 100.77, 102.24, 103.77, 105.24, 106.74]

# this video will be muted
video; media/hockey.mp4; start 0; end 10; fadein 5; volume 0; trim none

# the text will occur on top of the video (important that text comes after video)
video; media/lacy.mp4; start 0; end 10; fadeout 1.2; text; hello world; color red; fontsize 40; duration 10; position center; fadein 5

video; media/hockey.mp4; start 100; end 120

video; media/hockey.mp4; start 0; end 20

video; media/lacy.mp4; start 10; end 30; trim start

video; media/lacy.mp4; start 30; end 41; trim end

video; media/hockey.mp4; start 5; end 45

video; media/lacy.mp4; start 0; end 5; trim none

image; media/photo.png; duration 5; fadeout 5; position center; text; goodbye; duration 5; fadeout 5; position center; color purple; fontsize 50

```



## Prereqs

- Need `brew install imagemagick`


## To do

- Aspect ratio. [Maybe relevant](https://stackoverflow.com/questions/66775386/moviepy-distorting-concatenated-portrait-videos). In the meantime, when the aspect ratio gets messed up, just manually supply `height` or `width` for a clip.
- Fade text, `bg_color` needs to be transparent: [https://github.com/Zulko/moviepy/issues/400](https://github.com/Zulko/moviepy/issues/400). Possibly use masks?
- Include padding so that crossfades work. See [here](https://www.reddit.com/r/moviepy/comments/2f43e3/crossfades/).

