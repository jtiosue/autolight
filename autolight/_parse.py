import os
from . import Clip, CompositeClip, VideoClips, AudioClips
from typing import Tuple
import re

__all__ = "File", "parse_file", "write_file", "parse_and_write_file"


class File:
    def __init__(self, filename, **kwargs):
        self.filename = filename
        self.kwargs = kwargs.copy()


def parse_file(
    filename: str, base_directory="", options=None
) -> Tuple[AudioClips, VideoClips]:
    audio, video = AudioClips([]), VideoClips([])
    options = options or {}
    with open(os.path.join(base_directory, filename)) as f:
        # use add_directory_to_filename to change the base directory for this file
        all_lines = eval(add_directory_to_filenames(f.read().strip(), base_directory))
    for line in all_lines:
        # this doesn't work because if `end` is not provided in a video clip,
        # upon creation of a Clip object my code tries to find the clip and
        # determine the duration. That's why we instead use add_directory_to_filenaes
        # above to directly edit the string before evaluating.
        # if not isinstance(line, File) and "filename" in line:
        # line.filename = os.path.join(base_directory, line.filename)
        if isinstance(line, File):
            foptions = options | line.kwargs
            faudio, fvideo = parse_file(
                os.path.basename(line.filename),
                os.path.dirname(os.path.join(base_directory, line.filename)),
                foptions,
            )
            audio.extend(faudio)
            video.extend(fvideo)
        elif line.is_audio():
            for k, v in options.items():
                if k not in line:
                    setattr(line, k, v)
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


def add_directory_to_filenames(string: str, directory: str) -> str:
    """
    In the string, replace all occurrances of a filename by directory/filename.
    """

    def repl_equals(x):
        filename = re.search(r"['\"](.*?)['\"]", x.group()).group()[1:-1]
        return "filename='%s'" % os.path.join(directory, filename)

    def repl_dict(x):
        filename = re.search(r":\s*?['\"](.*?\..*?)['\"]", x.group()).group()
        filename = filename[1:].strip()[1:-1]
        return "'filename': '%s'" % os.path.join(directory, filename)

    string = re.sub(r"filename\s*?=\s*?['\"](.*?)['\"]", repl_equals, string)
    string = re.sub(r"['\"]filename['\"]\s*?:\s*?['\"](.*?)['\"]", repl_dict, string)

    # for the walrus

    def repl_equals_walrus(x):
        assignment = re.search(r"\(.*?\)", x.group()).group()[1:-1].strip()
        assignment = [x.strip() for x in assignment.split(":=")]
        var, filename = assignment
        filename = filename[1:-1]
        return "filename=(%s := '%s')" % (var, os.path.join(directory, filename))

    def repl_dict_walrus(x):
        assignment = re.search(r"\(.*?\)", x.group()).group()[1:-1].strip()
        assignment = [x.strip() for x in assignment.split(":=")]
        var, filename = assignment
        filename = filename[1:-1]
        return "'filename': (%s := '%s')" % (var, os.path.join(directory, filename))

    string = re.sub(
        r"filename\s*?=\s*?\(\s*?.*?\s*?:=\s*?['\"](.*?)['\"]\s*?\)",
        repl_equals_walrus,
        string,
    )
    string = re.sub(
        r"['\"]filename['\"]\s*?:\s*?\(\s*?.*?\s*?:=\s*?['\"](.*?)['\"]\s*?\)",
        repl_dict_walrus,
        string,
    )

    return string
