from autolight import auto_generate_from_csv, generate_from_csv, audioticks
import sys

if __name__ == "__main__":
    arguments = sys.argv[1:]
    if len(arguments) == 2 and arguments[0].strip() in ("generate", "autogenerate"):
        command, filename = arguments[0].strip(), arguments[1].strip()
        if command == "generate":
            generate_from_csv(filename)
        else:
            auto_generate_from_csv(filename)
    elif len(arguments) == 1 and arguments[0] == "audioticks":
        audioticks()
    else:
        print(
            "USAGE: python -m autolight [command] [file] \n"
            "command=generate or autogenerate or audioticks"
        )
