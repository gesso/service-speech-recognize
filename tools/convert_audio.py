#!/usr/bin/env python3
import os
import sys

# TODO: Merge with extract_audio.py
 
def convert_wma_to_mp3(filename):
    if not filename.lower().endswith('.wma'):
      raise Exception('Missing .wma extension.')
    os.system(f"ffmpeg -i {filename} -acodec libmp3lame -ab 128k {filename[:-4]}.mp3")
    

def convert_wav_to_mp3(filename):
    if not filename.lower().endswith('.wav'):
      raise Exception('Missing .wav extension.')
    print(f"ffmpeg -i {filename} -acodec libmp3lame -ab 128k {filename[:-4]}.mp3")
    os.system(f"ffmpeg -i {filename} -acodec libmp3lame -ab 128k {filename[:-4]}.mp3")


_file_format_converters = {
  'wma': convert_wma_to_mp3,
  'wav': convert_wav_to_mp3
}


def convert_audio(filename):
    (root, ext) = os.path.splitext(filename)
    if ext[1:].lower() not in _file_format_converters:
        raise Exception(f'Unsupported file format {ext}.')
    converter = _file_format_converters[ext[1:]]
    converter(filename)


if __name__ == '__main__':
    # os.path.dirname(os.path.abspath(__file__))
    filename = sys.argv[1]
    filename = os.path.abspath(filename)

    if not os.path.exists(filename):
        print(f'File {filename} does not exist.')
        sys.exit(1)

    try:
        convert_audio(filename)
    except Exception as e:
        print(f'Error: {e}')