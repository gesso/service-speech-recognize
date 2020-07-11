#!/usr/bin/env python3
import os
import sys
import argparse

from common.tools import compute_digest

BASE_PATH = os.path.join(os.path.expanduser("~"), '.sequencer')
MEDIA_PATH = os.path.join(BASE_PATH, "input")
MEDIA_INDEX_PATH = os.path.join(BASE_PATH, "media.index.csv")

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

    return parser.parse_args()


def import_media(input_media=None):
    # Initialize media index.
    if not os.path.exists(MEDIA_INDEX_PATH):
        f_media_index = open(MEDIA_INDEX_PATH, "w+")
        f_media_index.write("digest\tformat\tfilename\n")
        f_media_index.close()

    # TODO: Verify input_media is a file.

    input_abspath = os.path.abspath(input_media)
    input_digest = compute_digest(input_abspath)

    input_basepath, input_extension = os.path.splitext(input_media)
    input_basename = os.path.basename(input_basepath)
    input_format = input_extension[1:]

    # Validate input.
    if input_format not in ["wav", "mp3", "mp4"]:
        raise Exception(f"Unsupported input format {input_format}.")

    # Import media.
    import_abspath = os.path.join(MEDIA_PATH, f"{input_digest}.{input_format}")
    os.system(f'cp "{input_abspath}" "{import_abspath}"')

    # Prevent duplicates.
    with open(MEDIA_INDEX_PATH, 'r') as f_media_index:
        media_item = f_media_index.readline()
        while media_item:
            columns = media_item.split('\t')
            media_abspath = columns[1]
            media_digest = str(columns[0]).strip()
            if media_digest == input_digest:
                raise Exception(f"Already imported digest {media_digest} from {media_abspath}.")
            media_item = f_media_index.readline()

    # Index media.
    with open(MEDIA_INDEX_PATH, 'a') as f_media_index:
        f_media_index.write(f'{input_digest}\t{input_format}\t"{input_basename}"\n')
        print(f'{input_digest}\t"{input_media}"')


if __name__ == "__main__":
    options = parse_options(sys.argv)
    try:
        import_media(input=options.input)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
