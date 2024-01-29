from . import VideoClips, AudioClips, Clip, CompositeClip, get_file_info


__all__ = "generate_file_moviepy", "generate_clip_moviepy"

RESOLUTION_WIDTHS = {240: 426, 360: 640, 480: 854, 540: 960, 720: 1280, 1080: 1920}


def generate_file_moviepy(
    output_filename: str, audio: AudioClips = None, video: VideoClips = None
) -> None:
    import moviepy.editor as mp

    if not audio and not video:
        return
    elif not audio:
        audio = AudioClips([])
    elif not video:
        video = VideoClips([])

    if audio and audio[0].padding:
        raise ValueError("First audio cannot have a nonzero padding")
    elif video and video[0].padding:
        raise ValueError("First video cannot have a nonzero padding")

    mp_audio = []
    for c in audio:
        if not c.padding:
            mp_audio.append(generate_clip_moviepy(c))
        else:
            mp_audio[-1] = concatenate_with_padding(
                mp_audio[-1], generate_clip_moviepy(c), c.padding, True
            )

    mp_video = []
    for c in video:
        if not c.padding:
            mp_video.append(generate_clip_moviepy(c))
        else:
            mp_video[-1] = concatenate_with_padding(
                mp_video[-1], generate_clip_moviepy(c), c.padding, False
            )

    # compose is important for when the video/images have different sizes
    # https://stackoverflow.com/questions/74170641/is-there-an-issue-with-moviepys-concatenate-videoclips-function-or-is-my-imp
    if mp_video:
        mp_video = mp.concatenate_videoclips(mp_video)  # method="compose")
        if mp_audio:
            mp_audio = mp.concatenate_audioclips(mp_audio)
            if mp_video.audio:
                mp_audio = mp.CompositeAudioClip([mp_audio, mp_video.audio])
            mp_video.audio = mp_audio

        # https://www.reddit.com/r/moviepy/comments/3uwuub/no_sound/
        mp_video.write_videofile(
            output_filename + ".mp4",
            # fps=24,
            # threads=16?,
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            codec="libx264",
            audio_codec="aac",
        )
    elif mp_audio:
        mp_audio = mp.concatenate_audioclips(mp_audio)
        mp_audio.write_audiofile(output_filename + ".mp3")


def concatenate_with_padding(clip1, clip2, padding, audio=False, after=True):
    import moviepy.editor as mp

    # https://www.reddit.com/r/moviepy/comments/2f43e3/crossfades/
    f = mp.CompositeAudioClip if audio else mp.CompositeVideoClip
    return f(
        [
            clip1,
            clip2.set_start((clip1.end if after else clip1.start) + padding),
        ]
    )

    # return mp.concatenate_videoclips(
    #     [video1, video2],
    #     method="compose",
    #     bg_color=None,
    #     padding=padding,
    # )


def generate_clip_moviepy(clip: Clip):
    import moviepy.editor as mp

    afx, vfx = mp.afx, mp.vfx

    clip = clip.copy()

    if type(clip) == CompositeClip:
        mp_clip = generate_clip_moviepy(clip[0])
        for i in range(1, len(clip)):
            c = clip[i]
            mp_clip = concatenate_with_padding(
                mp_clip, generate_clip_moviepy(c), c.padding, clip.is_audio(), False
            )
        return mp_clip

    kind_to_class = dict(
        video=mp.VideoFileClip,
        audio=mp.AudioFileClip,
        text=mp.TextClip,
        image=mp.ImageClip,
    )

    if clip.is_text():
        kwargs = {}
        for key in (
            "color",
            "fontsize",
            "font",
            "bg_color",
            "stroke_width",
        ):  # add more
            # if key in clip:
            #     kwargs[key] = getattr(clip, key)
            kwargs[key] = clip[key]  # will get the default if nothing was supplied
            # kwargs[key] = getattr(clip, key) # same thing as kwargs[key] = clip[key]
        mp_elem = kind_to_class[clip.kind](clip.text, **kwargs)
    else:
        mp_elem = kind_to_class[clip.kind](clip.filename)

    if not clip.is_audio():
        mp_elem = mp_elem.set_position(("center", "center"))

    if "duration" in clip:
        mp_elem = mp_elem.set_duration(clip.duration)
    if "fps" in clip:
        mp_elem = mp_elem.set_fps(clip.fps)
    if "start" in clip or "end" in clip:
        mp_elem = mp_elem.subclip(clip.start, clip.end)
    if "fadein" in clip:
        fadein = afx.audio_fadein if clip.is_audio() else vfx.fadein
        mp_elem = mp_elem.fx(fadein, clip.fadein)
    if "fadeout" in clip:
        fadeout = afx.audio_fadeout if clip.is_audio() else vfx.fadeout
        mp_elem = mp_elem.fx(fadeout, clip.fadeout)
    if "position" in clip:
        mp_elem = mp_elem.set_position(clip.position)
    if "volume" in clip:
        mp_elem = mp_elem.fx(afx.volumex, clip.volume)
    if "crossfadein" in clip:
        mp_elem = mp_elem.crossfadein(clip.crossfadein)
    if "crossfadeout" in clip:
        mp_elem = mp_elem.crossfadeout(clip.crossfadeout)

    if clip.portrait:
        clip.rotate -= 90
        # mp_elem = mp_elem.rotate(-90, expand=False)
    if "rotate" in clip:
        # https://github.com/Zulko/moviepy/issues/1042
        # mp_elem = mp_elem.add_mask().rotate(clip.rotate, expand=False)
        mp_elem = mp_elem.rotate(clip.rotate, expand=False)

    if "height" in clip or "width" in clip:
        # there is an annoying bug in moviepy
        # https://stackoverflow.com/questions/76616042/attributeerror-module-pil-image-has-no-attribute-antialias
        import PIL

        PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
        if "width" in clip and "height" in clip:
            mp_elem = mp_elem.resize(newsize=(clip.width, clip.height))
        elif "width" in clip:
            mp_elem = mp_elem.resize(width=clip.width)
        else:
            mp_elem = mp_elem.resize(height=clip.height)
        height, width = mp_elem.size
    elif not clip.is_audio():
        height = clip.resolution
        if height not in RESOLUTION_WIDTHS:
            raise ValueError(
                "Resolution must be in %s" % list(RESOLUTION_WIDTHS.keys())
            )
        width = RESOLUTION_WIDTHS[height]
        # moviepy doesn't get actual height and width right, it includes black space.
        # I think it only happens because of the rotation above
        if "filename" in clip and clip.portrait:
            w, h = get_file_info(clip.filename, "PixelWidth"), get_file_info(
                clip.filename, "PixelHeight"
            )
            moviepy_w, moviepy_h = mp_elem.size
            shavew, shaveh = max(moviepy_w - w, 0), max(moviepy_h - h, 0)
            if shavew or shaveh:
                mp_elem = mp_elem.crop(
                    x1=int(shavew / 2),
                    y1=int(shaveh / 2),
                    x2=moviepy_w - int(shavew / 2),
                    y2=moviepy_h - int(shaveh / 2),
                )
        w, h = mp_elem.size

        if clip.is_image() or clip.is_video() and (width, height) != (w, h):
            # there is an annoying bug in moviepy
            # https://stackoverflow.com/questions/76616042/attributeerror-module-pil-image-has-no-attribute-antialias
            import PIL

            PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

            r = max(width / w, height / h)
            w, h = round(r * w), round(r * h)
            mp_elem = mp_elem.resize(
                newsize=(round(r * mp_elem.w), round(r * mp_elem.h))
            )

            if w > width:
                if "pan" not in clip:
                    clip.pan = "right"
            elif h > height:
                if "pan" not in clip:
                    clip.pan = "up"

    if "pan" in clip:
        # https://stackoverflow.com/questions/44225481/moviepy-crop-video-with-frame-region-of-interest-moving-from-left-to-right-w
        # https://practicalpython.yasoob.me/chapter8
        # https://moviepy-tburrows13.readthedocs.io/en/latest/_modules/moviepy/video/fx/scroll.html
        w, h = mp_elem.size
        xmax, ymax = w - width - 1, h - height - 1
        x_start, y_start = 0, 0
        x_speed, y_speed = (w - width) / clip.duration, (h - height) / clip.duration
        match clip.pan:
            case "right":
                y_speed = 0
            case "left":
                y_speed = 0
                x_start = xmax
                x_speed *= -1
            case "down":
                x_speed = 0
            case "up":
                x_speed = 0
                y_start = ymax
                y_speed *= -1
            case "center":
                x_speed, y_speed = 0, 0
                x_start, y_start = round(xmax / 2), round(ymax / 2)
            case "north":
                x_speed, y_speed = 0, 0
                x_start, y_start = round(xmax / 2), 0
            case "south":
                x_speed, y_speed = 0, 0
                x_start, y_start = round(xmax / 2), ymax
            case "east":
                x_speed, y_speed = 0, 0
                x_start, y_start = xmax, round(ymax / 2)
            case "west":
                x_speed, y_speed = 0, 0
                x_start, y_start = 0, round(ymax / 2)
            case _:
                raise ValueError("Unsupported pan: %s" % clip.pan)

        def fl(gf, t):
            x = int(max(0, min(xmax, x_start + round(x_speed * t))))
            y = int(max(0, min(ymax, y_start + round(y_speed * t))))
            return gf(t)[y : y + height, x : x + width]

        mp_elem = mp_elem.fl(fl, apply_to=["mask"])
        if "fps" in clip:
            mp_elem = mp_elem.set_fps(clip.fps)
        else:
            mp_elem = mp_elem.set_fps(60)  # panning is bad with less fps

        # if clip.pan == "right":
        #     # https://stackoverflow.com/questions/73521169/move-across-image-using-moviepy
        #     mp_elem = mp.CompositeVideoClip(
        #         [mp_elem.set_position(lambda t: (t * 10 + 50, "center"))]
        #     )
        # elif clip.pan == "left":
        #     mp_elem = mp.CompositeVideoClip(
        #         [mp_elem.set_position(lambda t: (-t * 10 - 50 + mp_elem.w, "center"))]
        #     )
        # elif clip.pan == "up":
        # mp_elem = mp.CompositeVideoClip(
        #     [mp_elem.set_position(lambda t: ("center", t * 10 + 50))]
        # )
        # elif clip.pan == "down":
        #     mp_elem = mp.CompositeVideoClip(
        #         [mp_elem.set_position(lambda t: ("center", -t * 10 - 50 + mp_elem.h))]
        #     )
        # else:
        #     mp_elem = mp.CompositeVideoClip([mp_elem.set_position(clip.pan)])

    if "zoom" in clip:
        if clip.zoom == "in":
            mp_elem = mp_elem.resize(lambda t: 1 + 0.1 * t)
        elif clip.zoom == "out":
            mp_elem = mp_elem.resize(lambda t: 1 + 0.1 * (mp_elem.duration - t))
        else:
            mp_elem = mp_elem.resize(clip.zoom)

    if "speed" in clip:
        mp_elem = mp_elem.speedx(clip.speed)

    if clip.debug and clip.kind in ("video", "image"):
        mp_elem = mp.CompositeVideoClip(
            [
                mp_elem,
                generate_clip_moviepy(
                    Clip(
                        text=clip.info,
                        bg_color="red",
                        color="black",
                        position=("right", "top"),
                        duration=clip.duration,
                        fps=5,
                        fontsize=16,
                    )
                ),
            ]
        )

    return mp_elem
