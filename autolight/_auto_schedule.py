from . import VideoClips, AudioClips
from typing import List


__all__ = ("auto_schedule",)


def auto_schedule(audio: AudioClips, video: VideoClips) -> None:
    """
    Edits audio and video in place
    """

    if not video or not audio:
        return

    mustticks = audio.mustticks
    mustmajorticks = mustticks + audio.majorticks
    allticks = mustmajorticks + audio.minorticks

    video = video.copy()
    video.reverse()

    ####
    current_time = 0
    while len(video) > 1:
        c = video[-1]

        if c.trimmable:
            # we can assume that each nontrim video gets trimmed by an averge of avg_tick_dist
            r = (
                audio.duration
                - current_time
                - video.nontrimmable_duration
                + video.num_nontrimmable * audio.avg_tick_dist(current_time)
            ) / video.trimmable_duration
            c.trim_clip(min(c.duration * r, c._videoduration))

        dist = lambda x: (
            abs(current_time + c.duration + c.padding - x)
            + 1000 * penalty(x, current_time, c)
        )

        tmust = min(mustticks, key=dist)
        tmajor = min(mustmajorticks, key=dist)
        tminor = min(allticks, key=dist)

        ### TO DO: IF WE PASSED A MUSTTICK WITHOUT TRANSITIONING,
        ### MANUALLY SPLIT THE CLIP AND JUMP A SECOND FORWARD

        if dist(tmust) <= 5:
            new_duration = tmust - current_time
            c.trim_clip(new_duration - c.padding)
        elif dist(tmajor) <= 3:
            new_duration = tmajor - current_time
            c.trim_clip(new_duration - c.padding)
        elif dist(tminor) <= 5:
            new_duration = tminor - current_time
            c.trim_clip(new_duration - c.padding)

        # else: if there are no ticks nearby, just go with the fixed point
        current_time += c.duration + c.padding

        video.pop()

    # for the last one, try to get it to match the audio duration
    c = video.pop()
    if current_time + c.padding >= audio.duration:
        c.trim_clip(2 - c.padding)
    else:
        c.trim_clip(min(audio.duration - current_time - c.padding, c._videoduration))


def penalty(t, current_time, clip):
    # returns 1 if making the clip last until time t is not possible.
    # otherwise returns 0
    duration = t - current_time - clip.padding
    return int(
        not (
            min(1.0, clip._videoduration / 2) <= duration <= clip._videoduration
            and t - current_time >= 0.1
        )
    )
