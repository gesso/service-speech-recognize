#!/usr/bin/env python3
import asyncio
import websockets
import sys
import json
import uuid
import hashlib
import os
import logging

logger = logging.getLogger('sequencer')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


from common.transcript import yield_event
# def yield_transcript_event(transcript_fn):
#     return 
    # with open(transcript_fn, 'r') as f:
    #     f.readline()
    #     line = f.readline()
    #     while line:
    #         values = line.split('\t')
    #         print(values)
    #         word = values[3]
    #         yield word
    #         line = f.readline()


def extract_concepts(transcript_fn, ignore_concepts=None):
    concepts = {}
    if not ignore_concepts:
        # ignore_concepts = ["a", "the"]
        ignore_concepts = []
    for event in yield_event(transcript_fn):
        concept = event['word']
        if concept in ignore_concepts:
            continue
        if concept in concepts:
            concepts[concept] = concepts[concept] + 1
        else:
            concepts[concept] = 1
    return concepts


def index_concepts(input_fn, output_fn=None):
    input_fp = os.path.abspath(input_fn)
    if not output_fn:
        output_fp = os.path.join(os.path.dirname(input_fp), 'concepts.csv')
    else:
        output_fp = os.path.abspath(output_fn)
    concepts = extract_concepts(input_fp)
    with open(output_fp, 'w') as f:
        f.write('concept_id\tconcept\tfrequency\n')
        for concept, concept_frequency in concepts.items():
            concept_id = uuid.uuid4()
            f.write(f'{concept_id}\t{concept}\t{concept_frequency}\n')


if __name__ == "__main__":
    transcript_fn = sys.argv[1]
    index_concepts(transcript_fn)
