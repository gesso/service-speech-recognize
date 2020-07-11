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


def parse_options(argv):
    parser = argparse.ArgumentParser(
        description='Create a transcript from input media.'
    )
    parser.add_argument(
        '--input-media',
        dest='input_media_fn',
        type=str,
        required=True,
        help='input media file'
    )
    parser.add_argument(
        '--input-transcript',
        dest='input_transcript_fn',
        type=str,
        required=True,
        help='input transcript file'
    )
    parser.add_argument(
        '--output',
        dest='output',
        required=False,
        help='output transcript file'
    )
    return parser.parse_args()


def sample_range():
    # TODO: Add this to support queries for arbitrary samples.
    pass
 

def extract_segment(
    input_media_fn,
    output_segment_fn=None,
    transcript_event=None,
    extract_timeout=60
):
    input_fp = os.path.abspath(input_media_fn)
    output_segment_ext = '.mp4'
    if not output_segment_fn:
        time_start = transcript_event[1]
        time_end = transcript_event[2]
        input_media_name, input_media_ext = os.path.splitext(os.path.basename(input_media_fn))
        output_segment_fn = f"{input_media_name}.{time_start}-{time_end}{output_segment_ext}"
        output_segment_fp = os.path.join(
            os.path.dirname(input_media_fn),
            output_segment_fn
        )
    else:
        output_segment_fp = os.path.abspath(output_segment_fn)

    if not os.path.exists(os.path.dirname(output_segment_fp)):
        os.makedirs(os.path.dirname(output_segment_fp))

    # HACK: to use time.strftime (doesn't support .%f)
    time_from = time.strftime(
        "%H:%M:%S.{}".format(transcript_event[1].split('.')[1]),
        time.gmtime(float(transcript_event[1]))
    )
    time_to = time.strftime(
        "%H:%M:%S.{}".format(transcript_event[2].split('.')[1]),
        time.gmtime(float(transcript_event[2]))
    )

    # TODO: Parallelize this command with generator (divide among processes or 
    #       nodes with generator, and aggregate result).
    t_start = time.time()
    try:
        p = subprocess.Popen(["ffmpeg", "-n", "-i", input_media_fn, "-ss", time_from, "-to", time_to, output_segment_fp],
                            shell=False,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    except Exception as e:
        # TODO: In container, output logs to syslogs.
        print(e, file=sys.stdout, flush=True)
    finally:
        t_elapsed = time.time() - t_start

    try:
        stdout, stderr = p.communicate(timeout=extract_timeout)
    except TimeoutExpired:
        p.kill()
        stdout, stderr = p.communicate()
        # TODO: Retry? Log?
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(e)

    extract_event = {
        'input': {
            # 'input_digest': input_digest,
            'time_from': time_from,
            'time_to': time_to
        },
        'output': {
            'filename': output_segment_fp
        },
        'metadata': {
            'time_elapsed': t_elapsed
        }
    }

    yield extract_event


def iterate_transcript(transcript_fn): # TODO: iterate_events?
    with open(transcript_fn, 'r') as f:
      f.readline()
      line = f.readline()
      while line:
          values = line.rstrip('\n').split('\t')
          yield values
          line = f.readline()


def extract_segments(media_fn, transcript_fn):
    for transcript_event in iterate_transcript(transcript_fn):
        for extract_event in extract_segment(
            media_fn,
            transcript_event=transcript_event
        ):
            # print(extract_event)
            # print(f"media segment from {extract_event['input']['time_from']} to {extract_event['input']['time_to']}.")
            # media_id, segment_id, timestamp, duration
            print(f"media segment from {extract_event['input']['time_from']} to {extract_event['input']['time_to']}.")
        # yield extract_event


def start_service():
    # TODO: Run as websocket service. Start server and expose I/O.
    # TODO: Pass service function to service wrapper?
    pass


if __name__ == "__main__":
    options = parse_options(sys.argv)
    # TODO: accept remote server port (optional), else try local server, else prompt to download and run container locally (if applicable).
    try:
        # transcript_fn = sys.argv[1]
        # input_source = 'youtube-dl:whatever_for_youtube-dl'
        # input_digest = '1485068cdd79cb9b5d3b79b1ed45180f9ae20afd17ce7b4c6caf59a84b3a9047'
        # input_fn = os.path.abspath(os.path.join('input', 'Plan_9_from_Outer_Space_1959.mp4'))
        # transcript_fn = os.path.abspath(os.path.join("output", input_digest, "transcript.csv"))
        extract_segments(
            options.input_media_fn,
            options.input_transcript_fn
        )
    except KeyboardInterrupt:
        exit(1)

else:
    start_service()