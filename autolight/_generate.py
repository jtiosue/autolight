import moviepy.editor as mp
from ._helpers import readlines, create_mp_element


def generate_from_file(filename: str) -> None:
    audio, video = [], []
    for line in readlines(filename):
        if len(line) == 1:
            mp_elem = create_mp_element(line[0])
            if line[0]["kind"] == "audio":
                if "padding" in line[0] and audio:
                    audio[-1] = concatenate_with_padding(audio[-1], mp_elem, line[0]["padding"], True)
                else:
                    audio.append(mp_elem)
            else:
                if "padding" in line[0] and video:
                    video[-1] = concatenate_with_padding(
                        video[-1], mp_elem, line[0]["padding"]
                    )
                else:
                    video.append(mp_elem)
        else:
            mp_elem = mp.CompositeVideoClip([create_mp_element(x) for x in line])
            if "padding" in line[0] and video:
                video[-1] = concatenate_with_padding(
                    video[-1], mp_elem, line[0]["padding"]
                )
            else:
                video.append(mp_elem)

    # compose is important for when the video/images have different sizes
    # https://stackoverflow.com/questions/74170641/is-there-an-issue-with-moviepys-concatenate-videoclips-function-or-is-my-imp
    mp_audio = mp.concatenate_audioclips(audio)
    if video:
        mp_video = mp.concatenate_videoclips(video, method="compose", bg_color=None)
        if mp_video.audio:
            mp_audio = mp.CompositeAudioClip([mp_audio, mp_video.audio])
        mp_video.audio = mp_audio

        # https://www.reddit.com/r/moviepy/comments/3uwuub/no_sound/
        mp_video.write_videofile(
            filename[:-3] + "mp4",
            # fps=24,
            # threads=16?,
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            codec="libx264",
            audio_codec="aac",
        )
    else:
        mp_audio.write_audiofile(filename[:-3] + "mp3")


def concatenate_with_padding(video1, video2, padding, audio=False):
    # https://www.reddit.com/r/moviepy/comments/2f43e3/crossfades/
    f = mp.CompositeAudioClip if audio else mp.CompositeVideoClip
    return f(
        [
            video1,
            video2.set_start(video1.end + padding),
        ]
    )

    # return mp.concatenate_videoclips(
    #     [video1, video2],
    #     method="compose",
    #     bg_color=None,
    #     padding=padding,
    # )
