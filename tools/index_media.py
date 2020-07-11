#!/usr/bin/env python3
import sys
import os
from datetime import datetime
import uuid
from elasticsearch import Elasticsearch

from common.tools import (
    compute_digest,
    get_output_dir
) 

es = Elasticsearch()

MEDIA_INDEX = 'media-index'


def index_media(media_fn, index_name=MEDIA_INDEX):
    print("indexing media")

    media = {
        'media_id': uuid.uuid4(),
        'media_digest': compute_digest(media_fn),
        'filename': os.path.basename(media_fn),
        'format': os.path.splitext(media_fn)[1],

        # 'duration': '',
        # 'keyframes': [],

        # TODO: name (e.g., Plan 9 from Outer Space)
    }

    index_response = es.index(
        index=index_name,
        # id=media_fn['event_id'],
        id=media['media_digest'],
        body=media
    )

    print(f"index_response: {index_response}")
    print(f"index_response['result']: {index_response['result']}")

    return index_response['_id']


def update_index(record, index_name=MEDIA_INDEX):
    pass


es.indices.create(index=MEDIA_INDEX, ignore=400)
es.indices.refresh(index=MEDIA_INDEX)


if __name__ == "__main__":
    media_fn = sys.argv[1]
    index_media(media_fn)
