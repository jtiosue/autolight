import os
from . import Clip, CompositeClip, VideoClips, AudioClips
from typing import Tuple
import re

__all__ = "File", "parse_file", "write_file", "parse_and_write_file"


class File(dict):
    def __init__(self, filename, **kwargs):
        super().__init__(filename=filename, **kwargs)
        self.kwargs = kwargs.copy()

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value


def parse_file(
    filename: str, options: dict = None, base_directory: str = ""
) -> Tuple[AudioClips, VideoClips]:
    audio, video = AudioClips([]), VideoClips([])
    options = options or {}
    convert_keys_to_seconds(options, base_directory)
    with open(os.path.join(base_directory, filename)) as f:
        # use add_directory_to_filename to change the base directory for this file
        # all_lines = eval(add_directory_to_filenames(f.read().strip(), base_directory))
        all_lines = eval(f.read().strip())
    for line in all_lines:
        # it is important to change the filename before converting the dicts to Clip
        # objects because the Clip object might try to figure out the duration of clip
        # upon intialization, which requires the filename to be correct.
        if isinstance(line, list):
            for l in line:
                convert_keys_to_seconds(l, base_directory)
            # options | l means will concatenate the two.
            # if there are overlaps, the assignments in l are
            # given precedence.
            line = CompositeClip([Clip(**(options | l)) for l in line])
        else:
            convert_keys_to_seconds(line, base_directory)
            if not isinstance(line, File):
                # options | line means will concatenate the two.
                # if there are overlaps, the assignments in line are
                # given precedence.
                line = Clip(**(options | line))

        if isinstance(line, File):
            foptions = options | line.kwargs
            faudio, fvideo = parse_file(
                os.path.basename(line.filename),
                foptions,
                os.path.dirname(line.filename),
            )
            audio.extend(faudio)
            video.extend(fvideo)
        elif line.is_audio():
            audio.append(line)
        else:
            video.append(line)
    return audio, video


def write_file(
    output_filename: str, audio: AudioClips = None, video: VideoClips = None
):
    if not audio:
        audio = AudioClips([])
    if not video:
        video = VideoClips([])

    with open(output_filename, "w") as f:
        print("[", file=f)
        for c, end in audio.iter_with_endpoints():
            print(str(c), ", ", file=f)
            print("#", to_hms(round(end, 2)), audio.tick_type(end), file=f)

        print("\n", file=f)

        for c, end in video.iter_with_endpoints():
            print(str(c), ", ", file=f)
            print("#", to_hms(round(end, 2)), audio.tick_type(end), file=f)
        print("]", file=f)


def parse_and_write_file(filename: str, options: dict = None):
    audio, video = parse_file(filename, options)
    write_file("parsed_" + filename, audio, video)


def to_seconds(t):
    if isinstance(t, str):
        seconds = 0
        for part in t.split(":"):
            seconds = seconds * 60 + float(part)
        return seconds
    return t


def to_hms(seconds):
    fraction = seconds - int(seconds)
    seconds = int(seconds)
    hours = seconds // 3600
    seconds -= hours * 3600
    minutes = seconds // 60
    seconds -= minutes * 60
    s = f"{hours}:" if hours else ""
    s += f"{minutes}:" if hours or minutes else ""
    s += f"{round(seconds + fraction, 2)}"
    return s


def convert_keys_to_seconds(line, base_directory):
    if "filename" in line:
        line["filename"] = os.path.join(base_directory, line["filename"])
    for key in ("start", "end", "duration"):
        if key in line:
            line[key] = to_seconds(line[key])
    for key in ("minorticks", "majorticks"):
        if key in line:
            line[key] = [to_seconds(x) for x in line[key]]


### Add the directory to filenames by using regex.
# def add_directory_to_filenames(string: str, directory: str) -> str:
#     """
#     In the string, replace all occurrances of a filename by directory/filename.
#     """

#     def repl_equals(x):
#         filename = re.search(r"['\"](.*?)['\"]", x.group()).group()[1:-1]
#         return "filename='%s'" % os.path.join(directory, filename)

#     def repl_dict(x):
#         filename = re.search(r":\s*?['\"](.*?\..*?)['\"]", x.group()).group()
#         filename = filename[1:].strip()[1:-1]
#         return "'filename': '%s'" % os.path.join(directory, filename)

#     string = re.sub(r"filename\s*?=\s*?['\"](.*?)['\"]", repl_equals, string)
#     string = re.sub(r"['\"]filename['\"]\s*?:\s*?['\"](.*?)['\"]", repl_dict, string)

#     # for the walrus

#     def repl_equals_walrus(x):
#         assignment = re.search(r"\(.*?\)", x.group()).group()[1:-1].strip()
#         assignment = [x.strip() for x in assignment.split(":=")]
#         try:
#             var, filename = assignment
#         except ValueError:
#             raise ValueError("As of now, you can't have nested walruses: " + x.group())
#         filename = filename[1:-1]
#         return "filename=(%s := '%s')" % (var, os.path.join(directory, filename))

#     def repl_dict_walrus(x):
#         assignment = re.search(r"\(.*?\)", x.group()).group()[1:-1].strip()
#         assignment = [x.strip() for x in assignment.split(":=")]
#         try:
#             var, filename = assignment
#         except ValueError:
#             raise ValueError("As of now, you can't have nested walruses: " + x.group())
#         filename = filename[1:-1]
#         return "'filename': (%s := '%s')" % (var, os.path.join(directory, filename))

#     string = re.sub(
#         r"filename\s*?=\s*?\(\s*?.*?\s*?:=\s*?['\"](.*?)['\"]\s*?\)",
#         repl_equals_walrus,
#         string,
#     )
#     string = re.sub(
#         r"['\"]filename['\"]\s*?:\s*?\(\s*?.*?\s*?:=\s*?['\"](.*?)['\"]\s*?\)",
#         repl_dict_walrus,
#         string,
#     )

#     return string
