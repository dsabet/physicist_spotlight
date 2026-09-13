import sys
from spotlight import main

if __name__ == "__main__":
    sys.exit(main(["validate", *sys.argv[1:]]))
