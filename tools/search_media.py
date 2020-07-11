#!/usr/bin/env python3
"""
Examples:
python3 search_media.py "Alan"
"""
import sys
from datetime import datetime
from pprint import pprint
from elasticsearch import Elasticsearch

es = Elasticsearch()

MEDIA_INDEX = 'media-index'


def get_media(media_digest):
    index_response = es.get(index=MEDIA_INDEX, id=media_digest)
    pprint(index_response)
    # print(index_response['_source'])
    return index_response['_source']

    
def _search_match(query, limit=25):
    return es.search(
        index=MEDIA_INDEX,
        # body={"query": {"match_all": {}}} # get all
        size=limit,
        body={
            "query": {
                "match": {
                    'filename': {
                        "query": query,
                    }
                }
            }
            # "query": {
            #     "filtered": {
            #         "query": {
            #             "bool": {
            #                 "must": [
            #                     {
            #                         "match": {
            #                             'filename': query
            #                         }
            #                     }
            #                 ]
            #             }
            #         },
            #         "filter": {"term": {"word": "because"}}
            #     }
            # }
        }
    )

    
def _search_term(query, boost=1.0):
    return es.search(
        index=MEDIA_INDEX,
        body={
            "query": {
                "term": {
                    'filename': {
                        "value": query,
                        "boost": boost
                    } 
                }
            }
        }
    )


def _search_fuzzy(query, fuzziness=1):
    return es.search(
        index=MEDIA_INDEX,
        body={
            "query": {
                "fuzzy": {
                    'filename': {
                        "value": query,
                        "fuzziness": fuzziness
                    }
                }
            }
        }
    )
    

def search_media(query, search_type="match"):
    # https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html
    search_types = {
        "match": _search_match,
        "fuzzy": _search_fuzzy,
        "term": _search_term
    }
    if search_type not in search_types:
        raise Exception("Unsupported search type.")
    index_response = search_types[search_type](query)
    # hit_count = index_response['hits']['total']['value']
    # print("Got %d Hits:" % hit_count)
    events = []
    for hit in index_response['hits']['hits']:
        # print(hit)
        event = hit["_source"]
        events.append(event)
    return events


if __name__ == "__main__":
    query = sys.argv[1]

    print("\media_digest\tfilename")
    for transcript_event in search_media(query):
        media_digest = transcript_event['media_digest']
        media_filename = transcript_event['filename']
        print(f"{media_digest}\t{media_filename}")
