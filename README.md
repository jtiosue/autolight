# Autolight

Automatically make compilation highlight videos

## Usage

Create a CSV file as below named file.csv and a TXT as below named audio.txt. Then run `python -m autolight [auto]generate file.csv`.
If you don't include the `auto`, then the timestamps of the CSV file will be strictly adhered to.
If you do include auto, then autolight will algorithmically adjust timestamps to make a nice movie.


#### Without auto

**file.csv**

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

**file.csv**

```

```


**audio.txt**

The audio TXT file contains the file location of your desired audio file as well as the timestamps of good transition points. You can tap the timestamps out with `python -m autolight autoticks`.

```
~/Documents/cool-song.mp3,0,1.234
```



## Prereqs

- Need `brew install imagemagick`