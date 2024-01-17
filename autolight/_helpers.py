import moviepy.editor as mp

afx, vfx = mp.afx, mp.vfx


def readlines(filename: str):
    with open(filename) as f:
        for line in f:
            if not line.strip() or line.strip()[0] == "#":
                continue
            compiled_line = []
            l = [x.strip() for x in line.split(";")]
            i = 0
            while i < len(l):
                elem = l[i]
                if elem in ("audio", "video", "image", "text"):
                    compiled_line.append(dict(kind=elem))
                    i += 1
                    compiled_line[-1]["arg"] = l[i]

                elif elem.strip():
                    j = elem.index(" ")
                    compiled_line[-1][elem[:j].strip()] = try_number(elem[j:].strip())

                i += 1

            yield compiled_line


def try_number(string: str):
    try:
        output = int(string)
    except (ValueError, TypeError):
        try:
            output = float(string)
        except (ValueError, TypeError):
            output = string
    return output


def create_mp_element(line):
    kind_to_class = dict(
        video=mp.VideoFileClip,
        audio=mp.AudioFileClip,
        text=mp.TextClip,
        image=mp.ImageClip,
    )

    if line["kind"] == "text":
        kwargs = {}
        for key, value in line.items():
            if key in ("color", "fontsize", "font"):  # add more
                kwargs[key] = value
        mp_elem = kind_to_class[line["kind"]](line["arg"], **kwargs)
    else:
        mp_elem = kind_to_class[line["kind"]](line["arg"])

    if "duration" in line:
        mp_elem = mp_elem.set_duration(line["duration"])
    if "start" in line:
        mp_elem = mp_elem.subclip(line["start"], line["end"])
    if "fadein" in line:
        fadein = afx.audio_fadein if line["kind"] == "audio" else vfx.fadein
        mp_elem = mp_elem.fx(fadein, line["fadein"])
    if "fadeout" in line:
        fadeout = afx.audio_fadeout if line["kind"] == "audio" else vfx.fadeout
        mp_elem = mp_elem.fx(fadeout, line["fadeout"])
    if "position" in line:
        mp_elem = mp_elem.set_position(line["position"])
    if "volume" in line:
        mp_elem = mp_elem.fx(afx.volumex, line["volume"])

    return mp_elem
