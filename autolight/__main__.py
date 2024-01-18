from autolight import auto_generate_from_file, generate_from_file, audioticks
import sys

if __name__ == "__main__":
    arguments = sys.argv[1:]
    if len(arguments) == 2 and arguments[0].strip() in (
        "generate",
        "autogenerate",
        "audioticks",
    ):
        command, filename = arguments[0].strip(), arguments[1].strip()
        if command == "generate":
            generate_from_file(filename)
        elif command == "autogenerate":
            auto_generate_from_file(filename)
        elif command == "audioticks":
            audioticks(filename)
    elif len(arguments) == 1 and arguments[0].strip() == "audioticks":
        audioticks()
    else:
        print(
            "USAGE: python -m autolight [command] [file] \n"
            "command=generate or autogenerate or audioticks"
        )
