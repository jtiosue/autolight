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
    filename: str, base_directory="", options=None
) -> Tuple[AudioClips, VideoClips]:
    audio, video = AudioClips([]), VideoClips([])
    options = options or {}
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
                if "filename" in l:
                    l["filename"] = os.path.join(base_directory, l["filename"])
            line = CompositeClip([Clip(**l) for l in line])
        else:
            if "filename" in line:
                line["filename"] = os.path.join(base_directory, line["filename"])
            if not isinstance(line, File):
                line = Clip(**line)

        if isinstance(line, File):
            foptions = options | line.kwargs
            faudio, fvideo = parse_file(
                os.path.basename(line.filename),
                os.path.dirname(line.filename),
                foptions,
            )
            audio.extend(faudio)
            video.extend(fvideo)
        elif line.is_audio():
            for k, v in options.items():
                if k not in line:
                    setattr(line, k, v)
                    # same thing with setitem
                    # line[k] = v
            audio.append(line)
        else:
            for k, v in options.items():
                if k not in line:
                    setattr(line, k, v)
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
            print(f"# {round(end, 2)} {audio.tick_type(end)}", file=f)

        print("\n", file=f)

        for c, end in video.iter_with_endpoints():
            print(str(c), ", ", file=f)
            print(f"# {round(end, 2)} {audio.tick_type(end)}", file=f)
        print("]", file=f)


def parse_and_write_file(filename: str):
    audio, video = parse_file(filename)
    write_file("parsed_" + filename, audio, video)


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
