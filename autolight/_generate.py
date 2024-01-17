import moviepy.editor as mp
from ._helpers import readlines, create_mp_element


def generate_from_csv(filename: str) -> None:
    audio, video = [], []
    for line in readlines(filename):
        if len(line) == 1:
            mp_elem = create_mp_element(line[0])
            if line[0]["kind"] == "audio":
                audio.append(mp_elem)
            else:
                video.append(mp_elem)
        else:
            video.append(mp.CompositeVideoClip([create_mp_element(x) for x in line]))

    # compose is important for when the video/images have different sizes
    # https://stackoverflow.com/questions/74170641/is-there-an-issue-with-moviepys-concatenate-videoclips-function-or-is-my-imp
    mp_video = mp.concatenate_videoclips(video, "compose")
    mp_audio = mp.concatenate_audioclips(audio)
    mp_audio = mp.CompositeAudioClip([mp_audio, mp_video.audio])
    mp_video.audio = mp_audio

    # https://www.reddit.com/r/moviepy/comments/3uwuub/no_sound/
    mp_video.write_videofile(
        filename[:-3] + "mp4",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True,
        codec="libx264",
        audio_codec="aac",
    )
