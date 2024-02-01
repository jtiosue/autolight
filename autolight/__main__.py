from argparse import ArgumentParser
from autolight import (
    auto_generate_from_file,
    generate_from_file,
    audioticks,
    parse_and_write_file,
    auto_schedule_from_file,
)

if __name__ == "__main__":
    parser = ArgumentParser(
        prog="autolight",
        description="Run autolight functionality. Optional arguments are supplied globally to all clips",
    )
    parser.add_argument(
        "command",
        type=str,
        # help="Must be one of generate, autoschedule, autogenerate (same as running autoschedule and then generate on the new file), audioticks, or parse",
        choices=["generate", "autogenerate", "autoschedule", "audioticks", "parse"],
    )
    parser.add_argument("filename", type=str, help="The file to run the command on")
    parser.add_argument(
        "--debug", action="store_true", help="Whether or not to run in debug mode"
    )
    parser.add_argument("--resolution", type=int, help="The desired video resolution")
    parser.add_argument("--volume", type=float, help="The video/audio volume")
    parser.add_argument("--fps", type=int, help="The desired FPS")
    parser.add_argument(
        "--speed", type=float, help="Whether to speed up or slow down the video"
    )
    parser.add_argument("--fontsize", type=int, help="Fontsize of text")
    parser.add_argument("--font", type=str, help="Font family of text")
    parser.add_argument("--color", type=str, help="Font color of text")
    parser.add_argument("--stroke_width", type=int, help="Stroke width of text")
    parser.add_argument("--bg_color", type=str, help="Background color of text")
    parser.add_argument(
        "--rotate", type=int, help="Angle in degrees to rotate the video"
    )
    parser.add_argument(
        "--resize",
        action="store_true",
        help="Whether or not to check every video size against moviepy's calculation and fix a rare but occational moviepy bug",
    )
    parser.add_argument(
        "--trim",
        type=str,
        choices=["start", "end", "symmetric"],
    )
    parser.add_argument(
        "--trimmable",
        action="store_true",
        help="Whether to make videos trimmable for autoscheduling",
    )

    args = vars(parser.parse_args())
    command = args.pop("command")
    filename = args.pop("filename")
    options = {k: v for k, v in args.items() if v is not None}

    for k in ("debug", "resize", "trimmable"):
        if not options[k]:
            options.pop(k)

    match command:
        case "generate":
            generate_from_file(filename, options)
        case "autogenerate":
            auto_generate_from_file(filename, options)
        case "autoschedule":
            auto_schedule_from_file(filename, options)
        case "parse":
            parse_and_write_file(filename, options)
        case "audioticks":
            audioticks(filename)
