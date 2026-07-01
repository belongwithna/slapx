#!/usr/bin/env python3
import os
import sys

# Add the directory containing this script to the python path to resolve package imports correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from slapx.main import main

if __name__ == '__main__':
    main()
