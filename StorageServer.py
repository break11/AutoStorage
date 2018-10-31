#!/usr/bin/python3.7

# import re
import sys
import os

from StorageServer import main

if __name__ == '__main__':
    # sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])

    # sys.exit( main.main() ) # raise exception when debug in IDE
    main.main()
