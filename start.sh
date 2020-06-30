#!/bin/bash

# Start interactive session. Can be useful for debugging.
# docker run --rm -it -p 2700:2700 alphacep/kaldi-en:latest /bin/bash

# Start server.
docker run --rm -it -p 2700:2700 alphacep/kaldi-en:latest