#!/usr/bin/env python3

import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <markdown_file>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.is_file():
        print(f"Error: '{file_path}' does not exist or is not a file.")
        sys.exit(1)

    # Read file contents
    text = file_path.read_text(encoding="utf-8")

    # Convert all uppercase characters to lowercase
    text = text.lower()

    # Overwrite the original file
    file_path.write_text(text, encoding="utf-8")

    print(f"Converted '{file_path}' to lowercase.")


if __name__ == "__main__":
    main()
