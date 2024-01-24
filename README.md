# Autolight

Automatically make compilation highlight videos

- `python -m autolight audioticks filename.mp3` to generate a list of major and minor transition points.
- `python -m autolight parse filename.py` to take a list of audio and video clips and parse it into a nicer format with duration details.
- `python -m autolight generate filename.py` to take a list of audio and video clips and generate an mp4 from it.
- `python -m autolight autoschedule filename.py` to take a list of audio and video clips and generate a new `auto_filename.py` from it that is nicely compiled to the audio. You can then create the new video with `python -m autolight generate auto_filename.py`.
- `python -m autolight autogenerate filename.py` simply runs `python -m autolight autoschedule filename.py && python -m autolight generate auto_filename.py`.

See `examples/` for how to format `filename.py`.


## Notes

- Need `brew install imagemagick`
- For crossfading, do `crossfadein=2` and `padding=-2`.
- The current `get_file_duration` function only works for macs, but there are crossplatform ways of doing it that are commented out.
- For `File(filename='directory/file.py', someoptions=4)`, `someoptions=4` will be supplied to all Clips within `directory/file.py` except those that explicitly set something else for `someoptions`.
- For `File(filename='directory/file.py')`, when reading `directory/file.py`, the base directory will be changed to `directory` for all subsequent files. E.g. if in `directory/file.py` you have `Clip(filename="helloworld.mp4")`, then autolight will look for the `helloworld.mp4` file within `directory/`; i.e. it will look for the file `directory/helloworld.mp4`. To go back up a directory, you can put `Clip(filename="../helloworld.mp4")`. Then, autolight will look for `directory/../helloworld.mp4`, and so will just look for `helloworld.mp4` in the parent directory.


## To do

- Aspect ratio. [Maybe relevant](https://stackoverflow.com/questions/66775386/moviepy-distorting-concatenated-portrait-videos). In the meantime, when the aspect ratio gets messed up, just manually supply `height` or `width` for a clip.
- Fade text, `bg_color` needs to be transparent: [https://github.com/Zulko/moviepy/issues/400](https://github.com/Zulko/moviepy/issues/400). Possibly use masks?

