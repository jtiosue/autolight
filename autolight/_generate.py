from . import (
    generate_file_moviepy,
    generate_file_clips_moviepy,
    parse_file,
    write_file,
    auto_schedule,
    remove_filename_extension,
)

__all__ = "generate_from_file", "auto_schedule_from_file", "auto_generate_from_file"


def generate_from_file(filename: str, options: dict = None, clips: bool = False):
    audio, video = parse_file(filename, options=options)
    if not clips:
        generate_file_moviepy(remove_filename_extension(filename), audio, video)
    else:
        generate_file_clips_moviepy(remove_filename_extension(filename), audio, video)


def auto_schedule_from_file(filename: str, options: dict = None):
    audio, video = parse_file(filename, options=options)
    auto_schedule(audio, video)
    write_file("auto_" + filename, audio, video)


def auto_generate_from_file(filename: str, options: dict = None):
    auto_schedule_from_file(filename, options)
    generate_from_file("auto_" + filename)
