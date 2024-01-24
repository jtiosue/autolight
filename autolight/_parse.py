import os
from . import Clip, CompositeClip, VideoClips, AudioClips
from typing import Tuple

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
        all_lines = eval(f.read().strip())
        # to do: use re.sub here so that filename is converted to base_directory/filename.
    for line in all_lines:
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
