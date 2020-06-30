#!/usr/bin/env python3
import os
import sys
import argparse

from tools import compute_digest

HOME_PATH = os.path.join(os.path.expanduser("~"), '.sequencer')
INPUT_PATH = os.path.join(HOME_PATH, "input")

MEDIA_INDEX_PATH = os.path.join(HOME_PATH, "media.index.csv")

def parse_options(argv):
    parser = argparse.ArgumentParser(
        description='List input media.'
    )

    # Client arguments.
    parser.add_argument(
        'input',
        type=str,
        help='input media'
    )
    parser.add_argument(
        '--normalize',
        dest='normalize',
        required=False,
        action='store_true',
        help='normalize media filenames on disk'
    )
    parser.add_argument(
        '--no-copy',
        dest='no_copy',
        required=False,
        action='store_false',
        default=True,
        help='import without copying'
    )

    return parser.parse_args()


def import_media(input_fn=None):
    if not os.path.exists(MEDIA_INDEX_PATH):
        print(MEDIA_INDEX_PATH)
        f_media_index = open(MEDIA_INDEX_PATH, "w+")
        f_media_index.write("filename\tdigest\n")
        f_media_index.close()

    input_abspath = os.path.abspath(input_fn)
    input_digest = compute_digest(input_abspath)

    input_root, input_ext = os.path.splitext(input_fn)
    media_name = os.path.basename(input_root)
    media_format = os.path.basename(input_ext[1:])

    # Validate input.
    if media_format not in ["wav", "mp3", "mp4"]:
        raise Exception(f"Unsupported format {media_format}.")

    # Prevent duplicate.
    with open(MEDIA_INDEX_PATH, 'r') as f_media_index:
        media_item = f_media_index.readline()
        while media_item:
            columns = media_item.split('\t')
            media_abspath = columns[0]
            media_digest = str(columns[1]).strip()
            if media_digest == input_digest:
                raise Exception(f"Already imported digest {media_digest} from {media_abspath}.")
            media_item = f_media_index.readline()

    # Index media.
    with open(MEDIA_INDEX_PATH, 'a') as f_media_index:
        f_media_index.write(f'"{input_abspath}"\t{input_digest}\n')
        print(f'"{input_fn}"\t{input_digest}')


if __name__ == "__main__":
    options = parse_options(sys.argv)
    try:
        import_media(input_fn=options.input)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
