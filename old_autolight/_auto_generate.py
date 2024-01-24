from . import generate_from_file
from ._helpers import readlines, create_mp_element


#### with multiple audio files, the ticks seem to not be correct. It might be something with padding? Not sure.
#### Make sure it's using the full audio duration. (not sure though, hard to tell)


def auto_generate_from_file(filename: str) -> None:
    audio, video = [], []
    for line in readlines(filename):
        if len(line) == 1:
            line = line[0]
            if line["kind"] == "audio":
                if "majorticks" in line:
                    # line["majorticks"] = eval(line["majorticks"])
                    offset = line["majorticks"][0]
                    for i in range(1, len(line["majorticks"])):
                        line["majorticks"][i] += offset
                    line["majorticks"][0] = 0
                if "minorticks" in line:
                    # line["minorticks"] = eval(line["minorticks"])
                    offset = line["minorticks"][0]
                    for i in range(1, len(line["minorticks"])):
                        line["minorticks"][i] += offset
                    line["minorticks"][0] = 0
                audio.append(line)
            else:
                start = line.pop("start", 0)
                speed = line.pop("speed", 1)
                if "end" not in line:
                    line["end"] = start + line.get(
                        "duration", create_mp_element(line).duration- start
                    )
                # line["end"] will get modified later, but videoend does not
                line["videostart"] = start
                line["videoend"] = line["end"]
                line["start"] = start
                if speed != 1:
                    line["speed"] = speed
                if "trim" not in line:
                    line["trim"] = "symmetric"
                video.append(line)
        else:
            video.append([])
            for l in line:
                start = l.pop("start", 0)
                speed = l.pop("speed", 1)
                l["videostart"] = start
                if "end" not in l:
                    l["end"] = start + l.get(
                        "duration", create_mp_element(l).duration - start
                    )
                l["videoend"] = l["end"]
                l["start"] = start
                if speed != 1:
                    l["speed"] = speed
                if "trim" not in l:
                    l["trim"] = "symmetric"
                video[-1].append(l)

    # get all possible transition points
    majorticks, minorticks, prev = [-100], [-100], 0.0
    for line in audio:
        prev += line.get("padding", 0)
        majorticks.extend([prev + x for x in line.get("majorticks", [])])
        line.pop("majorticks", None)
        minorticks.extend([prev + x for x in line.get("minorticks", [])])
        line.pop("minorticks", None)
        prev += create_mp_element(line).duration
        line["TEMP_ending_time"] = prev
    total_audio_duration = prev

    all_ticks = list(sorted(set(minorticks + majorticks)))
    tick_diff = [all_ticks[i+1] - all_ticks[i] for i in range(len(all_ticks) - 1)]
    avg_tick_dist = sum(tick_diff) / len(tick_diff)

    # based on transition points and videos, make compilation
    # each video has a "trim" key. If "trim" is "none", then we do not trim at all.
    # If it is "symmetric", then we trim evenly from the start and end.
    # If it is "start", then we only trim the start.
    # If it is "end", then we only trim the end.

    # add up all the video lengths, trim the ones that are allowed to be trimmed
    # by the same percentage so that the total video length is roughly the audio length
    total_video_length, total_trim_video_length = 0, 0
    total_nontrim_video_length = 0
    for line in video:
        if isinstance(line, list):
            total_video_length += max(
                ((l["end"] - l["start"]) / l.get("speed", 1) + line[0].get("padding", 0) for l in line)
            )
            total_trim_video_length += max(
                [0]
                + [
                    (l["end"] - l["start"]) / l.get("speed", 1) + line[0].get("padding", 0)
                    for l in line
                    if l["trim"] != "none"
                ]
            )
            total_nontrim_video_length += max(
                [0]
                + [
                    (l["end"] - l["start"]) / l.get("speed", 1) + line[0].get("padding", 0)
                    for l in line
                    if l["trim"] == "none"
                ]
            ) - avg_tick_dist
            # we can assume that each nontrim video gets trimmed by an averge of avg_tick_dist
        else:
            total_video_length += (line["end"] - line["start"]) / line.get("speed", 1) + line.get("padding", 0)
            if line["trim"] != "none":
                total_trim_video_length += (
                    (line["end"] - line["start"]) / line.get("speed", 1) + line.get("padding", 0)
                )
            elif line["trim"] == "none":
                total_nontrim_video_length += (
                    (line["end"] - line["start"]) / line.get("speed", 1) + line.get("padding", 0)
                ) - avg_tick_dist
                # we can assume that each nontrim video gets trimmed by an averge of avg_tick_dist

    # total_nontrim_video_length = total_video_length - total_trim_video_length


    # shrink trimmable videos by r
    # TODO!!
    # figure out a better way to do this. It seems like for a lot of videos we end up
    # shrinking to much because of the transitions below.
    r = (total_audio_duration - total_nontrim_video_length) / total_trim_video_length

    ####
    current_time = 0
    for line in video[:-1]:
        if isinstance(line, list):
            # lmax = max(line, key=lambda x: ((x["end"] - x["start"]) / x.get("speed", 1)))
            lmax = line[0]
            if lmax["trim"] != "none":
                trim_video(lmax, r)
            t = min(
                majorticks,
                key=lambda x: abs(
                    current_time
                    + (lmax["end"]
                    - lmax["start"]) / lmax.get("speed", 1)
                    + lmax.get("padding", 0)
                    - x
                )
                + 1000 * penalty(x, current_time, lmax),
            )
            tminor = min(
                minorticks + majorticks,
                key=lambda x: abs(
                    current_time
                    + (lmax["end"]
                    - lmax["start"]) / lmax.get("speed", 1)
                    + lmax.get("padding", 0)
                    - x
                )
                + 1000 * penalty(x, current_time, lmax),
            )

            if (
                abs(
                    current_time
                    + (lmax["end"]
                    - lmax["start"]) / lmax.get("speed", 1)
                    + lmax.get("padding", 0)
                    - t
                ) + 1000 * penalty(t, current_time, lmax)
                <= 3
                and t > current_time + 0.05
            ):
                new_duration = t - current_time
                trim_video(lmax, None, new_duration - lmax.get("padding", 0))
            elif (
                abs(
                    current_time
                    + (lmax["end"]
                    - lmax["start"]) / lmax.get("speed", 1)
                    + lmax.get("padding", 0)
                    - tminor
                ) + 1000 * penalty(tminor, current_time, lmax)
                <= 5
                and tminor > current_time + 0.05
            ):
                new_duration = tminor - current_time
                trim_video(lmax, None, new_duration - lmax.get("padding", 0))
            # else: if there are no ticks nearby, just go with the fixed point
            current_time += (lmax["end"] - lmax["start"]) / lmax.get("speed", 1) + lmax.get("padding", 0)
            for l in line:
                if (l["end"] - l["start"]) / l.get("speed", 1) + l.get("padding", 0) > (lmax["end"] - lmax["start"]) / lmax.get("speed", 1) + lmax.get("padding", 0):
                    trim_video(l, None, (lmax["end"] - lmax["start"]) / lmax.get("speed", 1) + lmax.get("padding", 0) - l.get("padding", 0))

            if lmax["trim"] == "none":
                total_nontrim_video_length -= (lmax["videoend"] - lmax["videostart"]) / lmax.get("speed", 1) + lmax.get("padding", 0) - avg_tick_dist
            else:
                total_trim_video_length -= (lmax["videoend"] - lmax["videostart"]) / lmax.get("speed", 1) + lmax.get("padding", 0)
            r = (total_audio_duration - current_time - total_nontrim_video_length) / total_trim_video_length

        else:
            if line["trim"] != "none":
                trim_video(line, r)
            t = min(
                majorticks,
                key=lambda x: abs(
                    current_time
                    + (line["end"]
                    - line["start"]) / line.get("speed", 1)
                    + line.get("padding", 0)
                    - x
                )
                + 1000 * penalty(x, current_time, line),
            )
            tminor = min(
                minorticks + majorticks,
                key=lambda x: abs(
                    current_time
                    + (line["end"]
                    - line["start"]) / line.get("speed", 1)
                    + line.get("padding", 0)
                    - x
                )
                + 1000 * penalty(x, current_time, line),
            )

            if (
                abs(
                    current_time
                    + (line["end"]
                    - line["start"]) / line.get("speed", 1)
                    + line.get("padding", 0)
                    - t
                ) + 1000 * penalty(t, current_time, line)
                <= 3
                and t > current_time
            ):
                new_duration = t - current_time
                trim_video(line, None, new_duration - line.get("padding", 0))
            elif (
                abs(
                    current_time
                    + (line["end"]
                    - line["start"]) / line.get("speed", 1)
                    + line.get("padding", 0)
                    - tminor
                ) + 1000 * penalty(tminor, current_time, line)
                <= 5
                and tminor > current_time
            ):
                new_duration = tminor - current_time
                trim_video(line, None, new_duration - line.get("padding", 0))
            # else: if there are no ticks nearby, just go with the fixed point
            current_time += (line["end"] - line["start"]) / line.get("speed", 1) + line.get("padding", 0)

            if line["trim"] == "none":
                total_nontrim_video_length -= (line["videoend"] - line["videostart"]) / line.get("speed", 1) + line.get("padding", 0) - avg_tick_dist
            else:
                total_trim_video_length -= (line["videoend"] - line["videostart"]) / line.get("speed", 1) + line.get("padding", 0)
            r = (total_audio_duration - current_time - total_nontrim_video_length) / total_trim_video_length

    # to do: make this respect trim specifications
    line = video[-1]
    if isinstance(line, list):
        for l in line:
            l["end"] = l.get("speed", 1) * (
                l["start"] / l.get("speed", 1)
                - l.get("padding", 0)
                + total_audio_duration
                - current_time
            )
            l["end"] = l["end"] if l["end"] <= l["videoend"] else l["videoend"]
            l["end"] = l["end"] if l["end"] >= l["start"] else l["videoend"]
            if "duration" in l:
                l["duration"] = (l["end"] - l["start"]) / l.get("speed", 1)
    else:
        line["end"] = line.get("speed", 1) * (
            line["start"] / line.get("speed", 1)
            - line.get("padding", 0)
            + total_audio_duration
            - current_time
        )
        line["end"] = line["end"] if line["end"] <= line["videoend"] else line["videoend"]
        line["end"] = line["end"] if line["end"] >= line["start"] else line["videoend"]
        if "duration" in line:
            line["duration"] = (line["end"] - line["start"]) / line.get("speed", 1)

    ######
    # write new csv

    majorticks = list(sorted(set(round(x, 2) for x in majorticks if x != -100)))
    minorticks = list(sorted(set(round(x, 2) for x in minorticks if x != -100)))

    with open("auto_" + filename, "w") as f:
        # audio
        for line in audio:
            ending_time = round(line.pop("TEMP_ending_time"), 2)
            ticktype = ""
            if ending_time in majorticks:
                ticktype = "(majortick)"
            elif ending_time in minorticks:
                ticktype = "(minortick)"

            print(make_text_from_line(line), file=f)
            print("#", "time:", ending_time, ticktype, file=f)

        # now do video
        current_time = 0
        for line in video:
            if isinstance(line, list):
                # lmax = max(line, key=lambda x: ((x["end"] - x["start"]) / x.get("speed", 1)))
                lmax = line[0]
            else:
                lmax = line
            duration = (lmax["end"] - lmax["start"]) / lmax.get("speed", 1)
            current_time += duration + lmax.get("padding", 0)
            ticktype = ""
            if round(current_time, 2) in majorticks:
                ticktype = "(majortick)"
            elif round(current_time, 2) in minorticks:
                ticktype = "(minortick)"
            print(make_text_from_line(line), file=f)
            print("#", "time:", round(current_time, 2), ticktype, file=f)

        print("\n\n###### All majorticks ######\n# ", majorticks, file=f)
        print("\n\n###### All minorticks ######\n# ", minorticks, file=f)

    return generate_from_file("auto_" + filename)


def trim_video(line, r, new_duration=None):
    # if line["trim"] == "none":
    #     return
    duration = (line["end"] - line["start"]) / line.get("speed", 1)
    new_duration = (
        new_duration if new_duration is not None else min(duration * r, duration)
    )
    shave = (duration - new_duration) * line.get("speed", 1)
    if line["trim"] == "start":
        if line["start"] + shave >= line["videostart"]:
            line["start"] += shave
        else:
            line["start"] = line["videostart"]
            line["end"] = line["start"] + new_duration * line.get("speed", 1)
    elif line["trim"] == "end":
        if line["end"] - shave <= line["videoend"]:
            line["end"] -= shave
        else:
            line["end"] = line["videoend"]
            line["start"] = line["end"] - new_duration * line.get("speed", 1)
    else:  # symmetric
        if (
            line["start"] + shave / 2 >= line["videostart"]
            and line["end"] - shave / 2 <= line["videoend"]
        ):
            line["start"] += shave / 2
            line["end"] -= shave / 2
        elif line["start"] + shave / 2 < line["videostart"]:
            line["start"] = line["videostart"]
            line["end"] = line["start"] + new_duration * line.get("speed", 1)

        else:
            line["end"] = line["videoend"]
            line["start"] = line["end"] - new_duration * line.get("speed", 1)

    if "duration" in line:
        line["duration"] = new_duration

    if (
        line["end"] > line["videoend"]
        or line["start"] < line["videostart"]
        or line["end"] <= line["start"]
    ):
        raise ValueError("Video not long enough: " + str(line))


def penalty(t, current_time, line):
    #
    if t <= current_time + .05:
        return 1
    duration = t - current_time - line.get("padding", 0)
    if duration > (line["videoend"] - line["videostart"]) / line.get("speed", 1):
        return 1
    return 0


def make_text_from_line(line):
    if isinstance(line, list):
        return "; ".join([make_text_from_line(l) for l in line])
    if "duration" in line:
        line.pop("start")
        line.pop("end")
    text = line["kind"] + "; " + line["arg"] + "; "
    for key, value in line.items():
        if key not in ("kind", "arg", "trim", "ticks", "videoend", "videostart"):
            text += key + " " + str(value) + "; "
    return text
