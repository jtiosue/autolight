from autolight import (
    auto_generate_from_file,
    generate_from_file,
    audioticks,
    parse_and_write_file,
    auto_schedule_from_file,
)
import sys

if __name__ == "__main__":
    arguments = sys.argv[1:]
    if len(arguments) == 2 and arguments[0].strip() in (
        "generate",
        "autogenerate",
        "autoschedule",
        "audioticks",
        "parse",
    ):
        command, filename = arguments[0].strip(), arguments[1].strip()
        if command == "generate":
            generate_from_file(filename)
        elif command == "autogenerate":
            auto_generate_from_file(filename)
        elif command == "audioticks":
            audioticks(filename)
        elif command == "parse":
            parse_and_write_file(filename)
        elif command == "autoschedule":
            auto_schedule_from_file(filename)
    elif len(arguments) == 1 and arguments[0].strip() == "audioticks":
        audioticks()
    else:
        print(
            "USAGE: python -m autolight [command] [file] \n"
            "command=generate or autogenerate or autoschedule or audioticks or parse"
        )
