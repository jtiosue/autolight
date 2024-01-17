from . import generate_from_csv
from ._helpers import readlines, create_mp_element


def auto_generate_from_csv(filename: str) -> None:
    audio, video = [], []
    for line in readlines(filename):
        if len(line) == 1:
            line = line[0]
            if line["kind"] == "audio":
                if "majorticks" in line:
                    line["majorticks"] = eval(line["majorticks"])
                    offset = line["majorticks"][0]
                    for i in range(1, len(line["majorticks"])):
                        line["majorticks"][i] += offset
                    line["majorticks"][0] = 0
                if "minorticks" in line:
                    line["minorticks"] = eval(line["minorticks"])
                    offset = line["minorticks"][0]
                    for i in range(1, len(line["minorticks"])):
                        line["minorticks"][i] += offset
                    line["minorticks"][0] = 0
                audio.append(line)
            else:
                start = line.pop("start", 0)
                if "end" not in line:
                    line["end"] = start + line.get(
                        "duration", create_mp_element(line).duration - start
                    )
                # line["end"] will get modified later, but videoend does not
                line["videoend"] = line["end"]
                line["start"] = start
                if "trim" not in line:
                    line["trim"] = "symmetric"
                video.append(line)
        else:
            video.append([])
            for l in line:
                start = l.pop("start", 0)
                if "end" not in l:
                    l["end"] = start + l.get(
                        "duration", create_mp_element(l).duration - start
                    )
                l["videoend"] = l["end"]
                l["start"] = start
                if "trim" not in l:
                    l["trim"] = "symmetric"
                video[-1].append(l)

    # get all possible transition points
    majorticks, minorticks, prev = [-100], [-100], 0.0
    for line in audio:
        majorticks.extend([prev + x for x in line.get("majorticks", [])])
        line.pop("majorticks")
        minorticks.extend([prev + x for x in line.get("minorticks", [])])
        line.pop("minorticks")
        prev += create_mp_element(line).duration
    total_audio_duration = prev

    # based on transition points and videos, make compilation
    # each video has a "trim" key. If "trim" is "none", then we do not trim at all.
    # If it is "symmetric", then we trim evenly from the start and end.
    # If it is "start", then we only trim the start.
    # If it is "end", then we only trim the end.

    # add up all the video lengths, trim the ones that are allowed to be trimmed
    # by the same percentage so that the total video length is roughly the audio length
    total_video_length, total_trim_video_length = 0, 0
    for line in video:
        if isinstance(line, list):
            total_video_length += max((l["end"] - l["start"] for l in line))
            total_trim_video_length += max(
                [0] + [l["end"] - l["start"] for l in line if l["trim"] != "none"]
            )
        else:
            total_video_length += line["end"] - line["start"]
            if line["trim"] != "none":
                total_trim_video_length += line["end"] - line["start"]

    total_nontrim_video_length = total_video_length - total_trim_video_length
    # shrink trimmable videos by r
    r = (total_audio_duration - total_nontrim_video_length) / total_trim_video_length
    for line in video:
        if isinstance(line, list):
            for l in line:
                trim_video(l, r)
        else:
            trim_video(line, r)

    ####
    # Now everything is roughly the right length. We just need to do set the transitions
    # to the ticks. We just do it greedily.
    current_time = 0
    for line in video[:-1]:
        if isinstance(line, list):
            lmax = max(line, key=lambda x: x["end"] - x["start"])
            t = min(
                majorticks,
                key=lambda x: abs(current_time + lmax["end"] - lmax["start"] - x)
                + 1000 * int(x + lmax["start"] - current_time > lmax["videoend"]),
            )
            tminor = min(
                minorticks + majorticks,
                key=lambda x: abs(current_time + lmax["end"] - lmax["start"] - x)
                + 1000 * int(x + lmax["start"] - current_time > lmax["videoend"]),
            )

            if abs(current_time + lmax["end"] - lmax["start"] - t) <= 3:
                lmax["end"] = t + lmax["start"] - current_time
            elif abs(current_time + lmax["end"] - lmax["start"] - tminor) <= 5:
                lmax["end"] = tminor + lmax["start"] - current_time
            # else: if there are no ticks nearby, just go with the fixed point
            current_time += lmax["end"] - lmax["start"]
            for l in line:
                l["end"] = min(l["start"] + lmax["end"] - lmax["start"], l["end"])
                if "duration" in l:
                    l["duration"] = l["end"] - l["start"]
        else:
            t = min(
                majorticks,
                key=lambda x: abs(current_time + line["end"] - line["start"] - x)
                + 1000 * int(x + line["start"] - current_time > line["videoend"]),
            )
            tminor = min(
                minorticks + majorticks,
                key=lambda x: abs(current_time + line["end"] - line["start"] - x)
                + 1000 * int(x + line["start"] - current_time > line["videoend"]),
            )

            if abs(current_time + line["end"] - line["start"] - t) <= 3:
                line["end"] = t + line["start"] - current_time
            elif abs(current_time + line["end"] - line["start"] - tminor) <= 5:
                line["end"] = tminor + line["start"] - current_time
            # else: if there are no ticks nearby, just go with the fixed point
            if "duration" in line:
                line["duration"] = line["end"] - line["start"]
            current_time += line["end"] - line["start"]

    line = video[-1]
    if isinstance(line, list):
        for l in line:
            l["end"] = (
                l["start"] + total_audio_duration - current_time + 1
            )  # end a little after audio
            if "duration" in l:
                l["duration"] = l["end"] - l["start"]
    else:
        line["end"] = (
            line["start"] + total_audio_duration - current_time + 1
        )  # end a little after audio
        if "duration" in line:
            line["duration"] = line["end"] - line["start"]

    ######
    # write new csv

    with open("auto_" + filename, "w") as f:
        # audio
        for line in audio:
            print(make_text_from_line(line), file=f)

        # now do video
        for line in video:
            print(make_text_from_line(line), file=f)

    return generate_from_csv("auto_" + filename)


def trim_video(line, r):
    if line["trim"] == "none":
        return
    duration = line["end"] - line["start"]
    new_duration = min(duration * r, duration)
    shave = duration - new_duration
    if line["trim"] == "start":
        line["start"] += shave
    elif line["trim"] == "end":
        line["end"] -= shave
    else:  # symmetric
        line["start"] += shave / 2
        line["end"] -= shave / 2


def make_text_from_line(line):
    if isinstance(line, list):
        return "; ".join([make_text_from_line(l) for l in line])
    if "duration" in line:
        line.pop("start")
        line.pop("end")
    text = line["kind"] + "; " + line["arg"] + "; "
    for key, value in line.items():
        if key not in ("kind", "arg", "trim", "ticks", "videoend"):
            text += key + " " + str(value) + "; "
    return text[:-2]
