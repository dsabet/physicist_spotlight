import sys
from spotlight import main

if __name__ == "__main__":
    sys.exit(main(["duplicates", *sys.argv[1:]]))
