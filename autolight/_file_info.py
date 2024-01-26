import subprocess

__all__ = ("get_file_info",)


def get_file_info(filename: str, info: str) -> float:
    """
    info should be eg duration, height, or width
    """
    ## ffprobe or ffmpeg are fast and crossplatform but require installation
    # https://stackoverflow.com/questions/3844430/how-to-get-the-duration-of-a-video-in-python
    # time = subprocess.run(
    #     [
    #         "ffprobe",
    #         "-v",
    #         "error",
    #         "-show_entries",
    #         "format=duration",
    #         "-of",
    #         "default=noprint_wrappers=1:nokey=1",
    #         self.filename,
    #     ],
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.STDOUT,
    # )
    # or maybe
    #     # https://stackoverflow.com/questions/24975076/get-media-file-length-in-mac-terminal
    # ffmpeg -i input 2>&1 | grep "Duration"| cut -d ' ' -f 4 | sed s/,//
    # but need to brew install ffmpeg
    # return float(time.stdout)

    ## moviepy is crossplatform and we already use it in this project, but it's so slow.
    # import moviepy.editor as mp

    # if endswith_extensions(filename, {".mp3", ".m4a"}):
    #     return mp.AudioFileClip(filename).duration
    # return mp.VideoFileClip(filename).duration

    ## mdls is fast and doesn't require external software but only works on mac
    # https://stackoverflow.com/questions/13332268/how-to-use-subprocess-command-with-pipes
    cmd = "mdls %s | grep %s | awk '{ print $3 }'" % (filename, info)
    ps = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    output = ps.communicate()[0].strip()
    try:
        return float(output)
    except ValueError:
        raise ValueError(f"Could not find {filename} or info {info} not found")
