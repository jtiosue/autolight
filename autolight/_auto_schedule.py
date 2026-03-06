from . import VideoClips, AudioClips, CompositeClip


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

    remaining = video.copy()
    remaining.reverse()

    index = 1

    ####
    current_time = 0
    while len(remaining) > 1:
        c = remaining[-1]

        if c.trimmable:
            # we can assume that each nontrim video gets trimmed by an averge of avg_tick_dist
            r = (
                audio.duration
                - current_time
                - remaining.nontrimmable_duration
                + remaining.num_nontrimmable * audio.avg_tick_dist(current_time)
            ) / remaining.trimmable_duration
            c.trim_clip(min(c.duration * r, c._videoduration))

        dist = lambda x: (
            abs(current_time + c.duration + c.padding - x)
            + 1000 * penalty(x, current_time, c)
        )

        tmust = min(mustticks, key=dist)
        tmajor = min(mustmajorticks, key=dist)
        tminor = min(allticks, key=dist)

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

        next_time = current_time + c.duration + c.padding

        ### This is the musttick logic. Handling edge cases complicated the algorithm.
        ### One a first pass, just ignore this section; the rest of the algorithm is
        ### much easier to understand
        index = split_for_mustticks(video, mustticks, c, current_time, next_time, index)
        ### END musttick logic

        current_time = next_time

        remaining.pop()
        index += 1

    # for the last one, try to get it to match the audio duration
    # need to do something about if there is a must tick here
    c = remaining.pop()
    if current_time + c.padding >= audio.duration:
        c.trim_clip(2 - c.padding)
    else:
        c.trim_clip(min(audio.duration - current_time - c.padding, c._videoduration))
    next_time = current_time + c.duration + c.padding
    split_for_mustticks(video, mustticks, c, current_time, next_time, index)


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


def split_for_mustticks(
    video: VideoClips, mustticks, c, current_time, next_time, index
):
    interval_mustticks = [
        x for x in mustticks if current_time + 0.2 < x < next_time - 0.2
    ]
    if not interval_mustticks:
        return index

    interval_mustticks.sort()
    original_duration = c.duration
    c.trim_clip(min(c.duration + len(interval_mustticks), c._videoduration))
    delta = (c.duration - original_duration) / len(interval_mustticks)
    for t in interval_mustticks:
        newc = c.copy()
        if isinstance(newc, CompositeClip):
            newc = newc[0]

        c.end = c.start + t - current_time
        c.padding = 0
        c.fadeout = 0
        c.crossfadeout = 0

        newc.start = c.end + delta
        newc.fadein = 0
        newc.crossfadein = 0

        video.insert(index, newc)
        index += 1
        c = newc

        current_time = t

    return index
