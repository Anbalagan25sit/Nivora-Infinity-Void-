#!/usr/bin/env python3
"""
Python wrapper for open_spotify.ps1
"""

import subprocess
import sys

def main():
    result = subprocess.run(
        ["powershell", "-File", "open_spotify.ps1"],
        capture_output=True,
        text=True
    )

    print(result.stdout, end='')
    if result.stderr:
        print(result.stderr, end='', file=sys.stderr)

    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
