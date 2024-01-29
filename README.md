# Autolight

Automatically make compilation highlight videos

- `python -m autolight audioticks filename.mp3` to generate a list of major and minor transition points.
- `python -m autolight parse filename.py` to take a list of audio and video clips and parse it into a nicer format with duration details.
- `python -m autolight generate filename.py` to take a list of audio and video clips and generate an mp4 from it.
- `python -m autolight autoschedule filename.py` to take a list of audio and video clips and generate a new `auto_filename.py` from it that is nicely compiled to the audio. You can then create the new video with `python -m autolight generate auto_filename.py`.
- `python -m autolight autogenerate filename.py` simply runs `python -m autolight autoschedule filename.py && python -m autolight generate auto_filename.py`.

For each of the commands (except for `parse` and `audioticks`), you can supply optional keyword arguments; e.g. `--volume 0 --resolution 720 --debug`.

See `examples/` for how to format `filename.py`.


## Notes

- Need `brew install imagemagick`
- For crossfading, do `crossfadein=2` and `padding=-2`.
- The current `get_file_duration` function only works for macs, but there are crossplatform ways of doing it that are commented out.
- For `File(filename='directory/file.py', someoptions=4)`, `someoptions=4` will be supplied to all Clips within `directory/file.py` except those that explicitly set something else for `someoptions`.
- For `File(filename='directory/file.py')`, when reading `directory/file.py`, the base directory will be changed to `directory` for all subsequent files. E.g. if in `directory/file.py` you have `Clip(filename="helloworld.mp4")`, then autolight will look for the `helloworld.mp4` file within `directory/`; i.e. it will look for the file `directory/helloworld.mp4`. To go back up a directory, you can put `Clip(filename="../helloworld.mp4")`. Then, autolight will look for `directory/../helloworld.mp4`, and so will just look for `helloworld.mp4` in the parent directory.
- As per [moviepy](https://stackoverflow.com/questions/73418729/moviepy-textclip-set-color-to-rgb-value), use rgba values to make thing semitransparent: `color="rgba(255,0,0,.5)"`, where the last value is between 0 and 1.
- For portrait videos/pictures, you should set `portrait=True`. 
- Setting `resolution=540` or `720` or `1080` will automatically fit every video to that size, possibly adding a zoom and/or pan. By default, `resolution=720`. You can override this by automatically supplying `width, height, zoom, pan` keywords. `height` and/or `width` will override `resolution`.
- You can set meta info for a clip with the `info="stuff"` keyword argument. If you run autolight in debug mode, `"stuff"` will automatically appear in the upper right hand corner. In debug mode, resolution will automatically be set to 240 and fps to 10 unless they are manually specified in the file.


## To do

- Aspect ratio. [Maybe relevant](https://stackoverflow.com/questions/66775386/moviepy-distorting-concatenated-portrait-videos). In the meantime, when the aspect ratio gets messed up, just manually supply `height` or `width` for a clip.
- Fade text, `bg_color` needs to be transparent: [https://github.com/Zulko/moviepy/issues/400](https://github.com/Zulko/moviepy/issues/400). Possibly use masks?
- Fix zoom.
- I think width/height doesn't work. Only resolution works. That might be because I still need to keep `concatenate_videos` with `method='compose`. Not sure.
- Instead of needing to supply `portrait=True`, somehow check to see if moviepy automatically rotated the image/video for some reason.
- Deal with when a video is not the desired size; e.g. portrait video. It might already work, not sure, need to test.
- Allow a video option to be audio fade in. More generally, allow an option so that during a certain video or a certain part of a video, the music fades out a little while the audio from the video fade in a little, and then fades out while the music fades back in.
