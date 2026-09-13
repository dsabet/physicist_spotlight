import sys
from spotlight import main

if __name__ == "__main__":
    sys.exit(main(["append", *sys.argv[1:]]))
