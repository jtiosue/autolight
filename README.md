# Autolight

Automatically make compilation highlight videos

- `python -m autolight audioticks filename.mp3` to generate a list of major and minor transition points.
- `python -m autolight parse filename.py` to take a list of audio and video clips and parse it into a nicer format with duration details.
- `python -m autolight generate filename.py` to take a list of audio and video clips and generate an mp4 from it.
- `python -m autolight autogenerate filename.py` to take a list of audio and video clips and generate a new `auto_filename.py` from it that is nicely compiled to the audio. You can then create the new video with `python -m autolight generate auto_filename.py`.

See `examples/` for how to format `filename.py`.


## Notes

- Need `brew install imagemagick`
- For crossfading, do `crossfadein=2` and `padding=-2`.


## To do

- Aspect ratio. [Maybe relevant](https://stackoverflow.com/questions/66775386/moviepy-distorting-concatenated-portrait-videos). In the meantime, when the aspect ratio gets messed up, just manually supply `height` or `width` for a clip.
- Fade text, `bg_color` needs to be transparent: [https://github.com/Zulko/moviepy/issues/400](https://github.com/Zulko/moviepy/issues/400). Possibly use masks?
- See the comment `to do: use re.sub here so that filename is converted to base_directory/filename.` in `_parse.py`.

