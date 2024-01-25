from . import VideoClips, AudioClips, Clip, CompositeClip


__all__ = "generate_file_moviepy", "generate_clip_moviepy"


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
        mp_video = mp.concatenate_videoclips(mp_video, method="compose")
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


def concatenate_with_padding(
    clip1: Clip, clip2: Clip, padding, audio=False, after=True
):
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

    if type(clip) == CompositeClip:
        mp_clip = generate_clip_moviepy(clip[0])
        for i in range(1, len(clip)):
            c = clip[i]
            mp_clip = concatenate_with_padding(
                mp_clip, generate_clip_moviepy(c), c.padding, False, False
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
        for key in ("color", "fontsize", "font", "bg_color"):  # add more
            # if key in clip:
            #     kwargs[key] = getattr(clip, key)
            kwargs[key] = clip[key] # will get the default if nothing was supplied
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
    if "rotate" in clip:
        # https://github.com/Zulko/moviepy/issues/1042
        # mp_elem = mp_elem.add_mask().rotate(clip.rotate, expand=False)
        mp_elem = mp_elem.rotate(clip.rotate, expand=False)
    if "zoom" in clip:
        if clip.zoom == "in":
            mp_elem = mp_elem.resize(lambda t: 1 + 0.2 * t)
        if clip.zoom == "out":
            duration = clip
            mp_elem = mp_elem.resize(lambda t: 1 + 0.2 * (mp_elem.duration - t))
    if "pan" in clip:  # need to also do crop
        if clip.pan == "right":
            # https://stackoverflow.com/questions/73521169/move-across-image-using-moviepy
            mp_elem = mp.CompositeVideoClip(
                [mp_elem.set_position(lambda t: (t * 10 + 50, "center"))]
            )
        elif clip.pan == "left":
            mp_elem = mp.CompositeVideoClip(
                [mp_elem.set_position(lambda t: (-t * 10 - 50 + mp_elem.w, "center"))]
            )
        elif clip.pan == "up":
            mp_elem = mp.CompositeVideoClip(
                [mp_elem.set_position(lambda t: ("center", t * 10 + 50))]
            )
        elif clip.pan == "down":
            mp_elem = mp.CompositeVideoClip(
                [mp_elem.set_position(lambda t: ("center", -t * 10 - 50 + mp_elem.h))]
            )
    if "speed" in clip:
        mp_elem = mp_elem.speedx(clip.speed)

    return mp_elem
