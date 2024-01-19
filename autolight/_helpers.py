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

    if line["kind"] != "audio":
        mp_elem = mp_elem.set_position(("center", "center"))

    if "duration" in line:
        mp_elem = mp_elem.set_duration(line["duration"])
    if "fps" in line:
        mp_elem = mp_elem.set_fps(line["fps"])
    if "start" in line or "end" in line:
        start = line.get("start", 0)
        end = line.get("end", mp_elem.duration - start)
        mp_elem = mp_elem.subclip(start, end)
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
    if "crossfadein" in line:
        mp_elem = mp_elem.crossfadein(line["crossfadein"])
    if "crossfadeout" in line:
        mp_elem = mp_elem.crossfadeout(line["crossfadeout"])
    if "height" in line or "width" in line:
        # there is an annoying bug in moviepy
        # https://stackoverflow.com/questions/76616042/attributeerror-module-pil-image-has-no-attribute-antialias
        import PIL
        PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
        if "width" in line and "height" in line:
            mp_elem = mp_elem.resize(newsize=(line["width"], line["height"]))
        elif "width" in line:
            mp_elem = mp_elem.resize(width=line["width"])
        else:
            mp_elem = mp_elem.resize(height=line["height"])
    if "rotate" in line:
        # https://github.com/Zulko/moviepy/issues/1042
        # mp_elem = mp_elem.add_mask().rotate(line["rotate"], expand=False)
        mp_elem = mp_elem.rotate(line["rotate"], expand=False)
    if "zoom" in line:
        if line["zoom"] == "in":
            mp_elem = mp_elem.resize(lambda t: 1 + .2*t)
        if line["zoom"] == "out":
            duration = line
            mp_elem = mp_elem.resize(lambda t: 1 + .2*(mp_elem.duration - t))
    if "pan" in line:
        if line["pan"] == "right":
            # https://stackoverflow.com/questions/73521169/move-across-image-using-moviepy
            mp_elem = mp.CompositeVideoClip([mp_elem.set_position(lambda t: (t * 10 + 50, "center"))])
        elif line["pan"] == "left":
            mp_elem = mp.CompositeVideoClip([mp_elem.set_position(lambda t: (-t * 10 - 50 + mp_elem.w, "center"))])
        elif line["pan"] == "up":
            mp_elem = mp.CompositeVideoClip([mp_elem.set_position(lambda t: ("center", t * 10 + 50))])
        elif line["pan"] == "down":
            mp_elem = mp.CompositeVideoClip([mp_elem.set_position(lambda t: ("center", -t * 10 - 50 + mp_elem.h))])


    return mp_elem
