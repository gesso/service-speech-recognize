#!/usr/bin/env python3
"""
Extract samples from video for each transcript event.
"""
import asyncio
import websockets
import sys
import json
import hashlib
import time
import os
import subprocess
from subprocess import TimeoutExpired
import argparse
import glob


def parse_options(argv):
    parser = argparse.ArgumentParser(
        description='Create a transcript from input media.'
    )
    parser.add_argument(
        '--input',
        nargs='+',
        dest='input_fns',
        type=str,
        required=True,
        help='input media file'
    )
    parser.add_argument(
        '--output',
        dest='output_fn',
        required=False,
        help='concatinate media sequence file'
    )
    return parser.parse_args()


def sequence_segments(input_fns=[], output_fn=None):
    """
    :param input: input_segment_fns
    :param output: output_segment_fn 
    """

    # ffmpeg -i opening.mkv -i episode.mkv -i ending.mkv \
    #    -filter_complex "[0:v] [0:a] [1:v] [1:a] [2:v] [2:a] 
    #                     concat=n=3:v=1:a=1 [v] [a]" \
    #    -map "[v]" -map "[a]" output.mkv

    # ffmpeg -i ../data/media/Alan_Kay_on_Linux.1.53-2.31.mp4 \
    #        -i ../data/media/Alan_Kay_on_Linux.2.55-2.82.mp4 \
    #        -i ../data/media/Alan_Kay_on_Linux.2.82-3.18.mp4 \
    #        -i ../data/media/Alan_Kay_on_Linux.3.18-4.11.mp4 \
    #        -i ../data/media/Alan_Kay_on_Linux.13.89-5.67.mp4 \
    #        -filter_complex "[0:v] [0:a] [1:v] [1:a] [2:v] [2:a] concat=n=3:v=1:a=1 [v] [a]" \
    #        -map "[v]" -map "[a]" output.mp4

    # Expand input filepaths.
    input_fps = []
    for input_fn in input_fns:
        # Default output to first input.
        for input_fp in glob.glob(os.path.abspath(input_fn)):
            input_fps.append(input_fp)
    print(input_fps)
    print("\n\n")

    output_ext = '.mp4'
    if not output_fn:
        input_fp = os.path.abspath(input_fps[0]) # default output to first input
        input_media_name, input_media_ext = os.path.splitext(os.path.basename(input_fp))
        output_fn = f"{input_media_name}.sequence{output_ext}"
        # output_segment_fn = f"{input_media_name}.{time_start}-{time_end}{output_segment_ext}"
        output_segment_fp = os.path.join(
            os.path.dirname(input_fp),
            output_fn
        )
    else:
        output_segment_fp = os.path.abspath(output_fn)

    if not output_fn:
        pass
    else:
        output_segment_fp = os.path.abspath(output_fn)

    output_segment_fp = os.path.abspath(output_fn)
    print(f"output to {output_segment_fp}")

    # TODO: Parallelize this command with generator (divide among processes or 
    #       nodes with generator, and aggregate result).
    input_args = []
    filter_complex = ""  # TODO: Rename.
    i = 0
    for input_fp in input_fps:
        input_args.append("-i")
        input_args.append(f'"{input_fp}"')
        filter_complex = filter_complex + ' ' + f'[{i}:v] [{i}:a]'
        i = i + 1
    filter_complex = filter_complex.strip()
    # [0:v] [0:a] [1:v] [1:a] [2:v] [2:a]
    # input_args = [
    #     "-i", "../data/media/Alan_Kay_on_Linux.1.53-2.31.mp4",
    #     "-i", "../data/media/Alan_Kay_on_Linux.2.55-2.82.mp4",
    #     "-i", "../data/media/Alan_Kay_on_Linux.2.82-3.18.mp4",
    #     "-i", "../data/media/Alan_Kay_on_Linux.3.18-4.11.mp4",
    #     "-i", "../data/media/Alan_Kay_on_Linux.4.89-5.67.mp4",
    # ]
    ffmpeg_args = [
        "ffmpeg",
        "-y",
        *input_args,
        "-filter_complex", f'"{filter_complex} concat=n={len(input_fps)}:v=1:a=1 [v] [a]"',
        "-map", '"[v]"',
        "-map", '"[a]"', f'"{output_segment_fp}"'
    ]
    print("\n\n\n")
    print(" ".join(ffmpeg_args))
    print("\n\n\n")
    os.system(" ".join(ffmpeg_args))
    """
    try:
        p = subprocess.Popen(
            ffmpeg_args,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except Exception as e:
        # TODO: In container, output logs to syslogs.
        print(e, file=sys.stdout, flush=True)

    try:
        # extract_timeout = 60
        # stdout, stderr = p.communicate(timeout=extract_timeout)
        stdout, stderr = p.communicate()
    except TimeoutExpired:
        p.kill()
        stdout, stderr = p.communicate()
        # TODO: Retry? Log?
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(e)
    """


if __name__ == "__main__":
    options = parse_options(sys.argv)
    try:
        sequence_segments(input_fns=options.input_fns, output_fn=options.output_fn)
    except KeyboardInterrupt:
        exit(1)
