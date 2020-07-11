#!/usr/bin/env python3
"""
Extract audio from vinput_fne and convert to correct format.
"""
import asyncio
import websockets
import sys

import json

import hashlib
import os

import argparse

from common.tools import compute_digest


def parse_options(argv):
    parser = argparse.ArgumentParser(
        description='Extract audio from video.'
    )
    parser.add_argument(
        'input',
        # dest='input_fn',
        type=str,
        help='input video file'
    )
    parser.add_argument(
        '--output',
        dest='output',
        required=False,
        help='output audio file'
    )
    parser.add_argument(
        '--output-format',
        dest='output_format',
        required=False,
        help='output format'
    )
    return parser.parse_args()


def extract_audio(input_fn, output_fn=None, output_format='mp3'):
    input_fn = os.path.abspath(input_fn)
    input_root, input_ext = os.path.splitext(input_fn)
    if not output_fn:
        output_fn = os.path.join('/', 'tmp', 'output', f'audio.{output_format}')
    output_fn = os.path.abspath(output_fn)
    if not os.path.exists(os.path.dirname(output_fn)):
        os.makedirs(output_fn)
    if not output_fn.endswith(output_format):
        raise Exception(f"'output_fn' must end with '.{output_format}'.")
    if output_format == 'wav':
        os.system(f"ffmpeg -i '{input_fn}' -acodec pcm_s16le -ac 2 '{output_fn}'")
    elif output_format == 'mp3':
        os.system(f"ffmpeg -i '{input_fn}' -b:a 192K -vn '{output_fn}'")
    else:
        raise Exception(f"Unsupported file type {input_ext}")

    extract_event = {
        "input": {
            "filename": input_fn,
            "digest": compute_digest(input_fn)
        },
        "output": {
            "filename": output_fn,
            "format": output_format,
            "digest": compute_digest(output_fn)
        }
    }

    return extract_event


if __name__ == "__main__":
    # input_fn = sys.argv[1]
    options = parse_options(sys.argv)
    input_fn = options.input
    print(f'input: {input_fn}')
    extract_event = extract_audio(input_fn)
    # print(json.dumps(extract_event, indent=4, sort_keys=True))
    print(f"input: {extract_event['input']['filename']}")
    print(f"output: {extract_event['output']['filename']}")
