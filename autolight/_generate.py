from . import generate_file_moviepy, parse_file, write_file, auto_schedule

__all__ = "generate_from_file", "auto_generate_from_file"


def generate_from_file(filename: str):
    audio, video = parse_file(filename)
    generate_file_moviepy(remove_extension(filename), audio, video)


def auto_generate_from_file(filename: str):
    audio, video = parse_file(filename)
    auto_schedule(audio, video)
    write_file("auto_" + filename, audio, video)
    # generate_from_file("auto_" + filename)


def remove_extension(filename):
    r = filename[::-1]
    i = r.index(".") + 1
    return filename[:-i]
