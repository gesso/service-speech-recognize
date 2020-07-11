#!/usr/bin/env python3
import sys
import json
import os
from uuid import uuid4
import argparse

import asyncio
import websockets

from common.tools import (
    compute_digest,
    get_output_dir
) 

BASE_PATH = os.path.join(os.path.expanduser("~"), '.sequencer')
MEDIA_PATH = os.path.join(BASE_PATH, "input")
MEDIA_INDEX_PATH = os.path.join(BASE_PATH, "media.index.csv")

# Application service.
ASR_SERVICE_PROTOCOL = "ws"
# ASR_SERVICE_HOST = "localhost"
ASR_SERVICE_HOST = "10.0.0.37"
ASR_SERVICE_PORT = 2700

# ASR service.
SERVICE_PROTOCOL = "ws"
SERVICE_HOST = "localhost"
SERVICE_PORT = 2800


def parse_options(argv):
    parser = argparse.ArgumentParser(
        description='Create a transcript from input media.'
    )

    # Client arguments.
    parser.add_argument(
        '--input',
        dest='input_fn',
        type=str,
        required=False,
        help='input media file'
    )
    parser.add_argument(
        '--output',
        dest='output',
        required=False,
        help='output transcript file'
    )

    # Extract transcript service arguments.
    parser.add_argument(
        '--service-protocol',
        dest='service_protocol',
        required=False,
        default=os.environ.get('SERVICE_PROTOCOL', SERVICE_PROTOCOL),
        help='service protocol'
    )
    parser.add_argument(
        '--service-host',
        dest='service_host',
        required=False,
        default=os.environ.get('SERVICE_HOST', SERVICE_HOST),
        help='service host'
    )
    parser.add_argument(
        '--service-port',
        dest='service_port',
        required=False,
        default=os.environ.get('SERVICE_PORT', SERVICE_PORT),
        help='service port'
    )

    # Automatic speech recognition (ASR) service arguments.
    parser.add_argument(
        '--asr-service-protocol',
        dest='asr_service_protocol',
        required=False,
        default=os.environ.get('ASR_SERVICE_PROTOCOL', ASR_SERVICE_PROTOCOL),
        help='ASR service protocol'
    )
    parser.add_argument(
        '--asr-service-host',
        dest='asr_service_host',
        required=False,
        default=os.environ.get('ASR_SERVICE_HOST', ASR_SERVICE_HOST),
        help='ASR service host'
    )
    parser.add_argument(
        '--asr-service-port',
        dest='asr_service_port',
        required=False,
        default=os.environ.get('ASR_SERVICE_PORT', ASR_SERVICE_PORT),
        help='ASR service port'
    )
    return parser.parse_args()


async def transcribe_audio(
    input_fn=None,
    protocol=ASR_SERVICE_PROTOCOL,
    host=ASR_SERVICE_HOST,
    port=ASR_SERVICE_PORT
):

    asr_service_uri = f"{protocol}://{host}:{port}"
    print(asr_service_uri)

    input_digest = compute_digest(input_fn)
    output_dir = os.path.join('output', input_digest)

    print(f'Input digest: {input_digest}.')
    print(f'Output directory: {output_dir}.')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # <WRITE_METADATA>
    f_metadata = open(os.path.join(output_dir, 'metadata.json'), 'w+')
    metadata = {
        'input': {
            'filename': input_fn,
            # 'video_digest': input_file_hash,
            'audio_digest': input_digest
        }
    }
    f_metadata.write(json.dumps(metadata, indent=4, sort_keys=True))
    f_metadata.close()
    # </WRITE_METADATA>

    f_text = open(os.path.join(output_dir, 'text.txt'), 'w+')
    f_transcript = open(os.path.join(output_dir, 'transcript.csv'), 'w+')
    f_transcript.write(f"event_id\ttime_start\ttime_end\tword\tconfidence\n")
    # global word list
    # global word frequency
    # audio/video with given word + timestamp

    async with websockets.connect(asr_service_uri) as websocket:

        # ffpeg process - stream audio output
        proc = await asyncio.create_subprocess_exec(
            'ffmpeg', '-nostdin', '-loglevel', 'quiet', '-i', input_fn, '-ar', '8000', '-ac', '1', '-f', 's16le', '-',
            stdout=asyncio.subprocess.PIPE
        )

        # input and transcribe ffmpeg audio output stream
        while True:
            input_data = await proc.stdout.read(8000)

            if len(input_data) == 0:
                break

            await websocket.send(input_data)
            output_data = await websocket.recv()

            output = json.loads(output_data)

            if 'result' in output:
                f_text.write(str(output['text']) + '\n')

                results = output['result']
                for result in results:
                    event_id = str(uuid4())
                    confidence = str(result['conf'])
                    word = str(result['word'])
                    time_end = str(result['end'])
                    time_start = str(result['start'])
                    f_transcript.write(f"{event_id}\t{time_start}\t{time_end}\t{word}\t{confidence}\n")

            # print(output_data)

        await websocket.send('{"eof" : 1}')
        result = await websocket.recv()
        # print(result)

        await proc.wait()

    f_text.close()
    f_transcript.close()


def start():
    pass


def start_service(
    service_protocol,
    service_host,
    service_port
):
    # wait for requst via WebSockets
    while True:
        continue

    # TODO: Start WebSocket server and stream responses along with entity ID.

    # Execute command.
    asyncio.get_event_loop().run_until_complete(
        transcribe_audio(
            input_fn=options.input_fn,
            protocol=options.asr_service_protocol,
            host=options.asr_service_host,
            port=options.asr_service_port
        )
    )
    asyncio.get_event_loop().close()


if __name__ == "__main__":
    options = parse_options(sys.argv)

    if options.input_fn:
        print(f'input: {options.input_fn}')

        # TODO: Check if `input_media` is checksum (else try filename).

        """
        # Lookup input media.
        with open(MEDIA_INDEX_PATH, 'r') as f_media_index:
            media_item = f_media_index.readline()
            while media_item:
                columns = media_item.split('\t')
                media_abspath = columns[1]
                media_digest = str(columns[0]).strip()
                if media_digest == input_digest:
                    raise Exception(f"Already imported digest {media_digest} from {media_abspath}.")
                media_item = f_media_index.readline()
        """

        # TODO: accept remote server port (optional),
        #       else try local server,
        #       else prompt to download and run container locally (if applicable).
        try:
            asyncio.get_event_loop().run_until_complete(
                transcribe_audio(
                    input_fn=options.input_fn,
                    protocol=options.asr_service_protocol,
                    host=options.asr_service_host,
                    port=options.asr_service_port
                )
            )
            asyncio.get_event_loop().close()

        except KeyboardInterrupt:
            exit(1)

    else:
        print('Starting service.')
        service_protocol = options.service_protocol
        service_host = options.service_host
        service_port = options.service_port
        try:
            start_service(service_protocol, service_host, service_port)
        except:
            print('Stopping service.')