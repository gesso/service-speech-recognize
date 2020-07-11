A simple server based on [Vosk-API](https://github.com/alphacep/vosk-api).

There are three implementations for different protocol - websocket, grpc, mqtt.

# Usage

There are multiple ways to use Sequencer. These may be omitted to simplify
the server.

1. Command line
2. WebSockets
1. REST API

## API

### Operations

- upload media (video)
- download media (video)
- create a sequence
- create a sample
- add sample or (sub-)sequence to sequence
- 

### CLI API (Command line usage)

The following commands correspond to the operations above.

#### Preliminary (media management) 

- `convert_video.py` (unnecessary building block for system?)
- `extract_audio.py`
- `convert_audio.py`

#### Essential

- `extract_transcript.py`

#### Extractors (Optional)

- `extract_concepts.py`
- `extract_video_samples.py`
- `extract_audio_samples.py`
- ???
- `find_semantic_relationships.py`

#### Generators (Optional)

These enable compound/recursive extraction, generation, and indexing
by outputing additional input. This is a feedback mechanism. The feedback
relates to the input used to generate it by some semantic relationship
(which may not be obvious).

- `generate_elaboration.py`
- `generate_questions.py`

#### Aggregators (Optional)

- `aggregate_concepts.py`

#### Store

- `index_transcript.py`

### HTTP API

**TODO**

### WebSockets API

**TODO**


### Start the service

Start the server:

```bash
./start.sh
```

Manually run the Docker container  with an English model to detect English 
words in an audio recording or stream:

```bash
docker run -d -p 2700:2700 alphacep/kaldi-en:latest
```

### Use the service

#### Transcribe an audio recording

Run the following command to transcribe an audio file:

```bash
git clone https://github.com/alphacep/vosk-server
cd vosk-server/websocket
./test.py test.wav
```

You can try with any wav file which has proper format - 8khz 16bit mono PCM.
Other formats has to be converted before decoding.

#### Transcribe live microphone audio input stream

You would need to install the pyaudio pip package:

```bash
pip install pyaudio
```

Start listening for microphone input, speak English, and observe the 
recognized words:

```bash
./test_microphone.py localhost:2700

Connected to ws://localhost:2700
Type Ctrl-C to exit
{"partial" : ""}
{"partial" : "поднимите мне веки"}
{"partial" : "поднимите мне веки"}
{"result" : [ {"word": "поднимите", "start" : 3.45, "end" : 4.26, "conf" : 1},
{"word": "мне", "start" : 4.26, "end" : 4.47, "conf" : 1},
{"word": "веки", "start" : 4.47, "end" : 5.07, "conf" : 1}
 ], "text" : "поднимите мне веки" }
{"partial" : ""}
Closing PyAudio Stream
Terminating PyAudio object
Terminating connection
{"result" : [  ], "text" : "" }
Bye
```
