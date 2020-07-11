#!/usr/bin/env python3
"""
Examples:
python3 search_events.py "crawling on around"
"""
import sys
from datetime import datetime
from pprint import pprint
from elasticsearch import Elasticsearch

es = Elasticsearch()

TRANSCRIPT_INDEX = 'transcript-index'


def get_transcript_event(document_id):
    index_response = es.get(index=TRANSCRIPT_INDEX, id=document_id)
    pprint(index_response)
    # print(index_response['_source'])
    return index_response['_source']

    
def _search_match(query, limit=25):
    return es.search(
        index=TRANSCRIPT_INDEX,
        # body={"query": {"match_all": {}}} # get all
        size=limit,
        body={
            "query": {
                "match": {
                    'last_10': {
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
            #                             'last_10': query
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
        index=TRANSCRIPT_INDEX,
        body={
            "query": {
                "term": {
                    'last_10': {
                        "value": query,
                        "boost": boost
                    } 
                }
            }
        }
    )


def _search_fuzzy(query, fuzziness=1):
    return es.search(
        index=TRANSCRIPT_INDEX,
        body={
            "query": {
                "fuzzy": {
                    'last_10': {
                        "value": query,
                        "fuzziness": fuzziness
                    }
                }
            }
        }
    )
    

def search_events(query, search_type="match"):
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

    sequence_time_start = None
    sequence_time_end = None
    print("\nevent_id\ttime_start\ttime_end\tword\tconfidence")
    for transcript_event in search_events(query):
        event_id = transcript_event['event_id']
        time_start = float(transcript_event['time_start'])
        time_end = float(transcript_event['time_end'])
        word = transcript_event['word']
        confidence = float(transcript_event['confidence'])
        print(f"{event_id}\t{time_start}\t{time_end}\t{word}\t{confidence}")

        # Update sequence.
        if not sequence_time_start or time_start < sequence_time_start:
            sequence_time_start = time_start
        if not sequence_time_end or time_end > sequence_time_end:
            sequence_time_end = time_end

    print("\nsequence:")
    print(f"time_start: {sequence_time_start}")
    print(f"time_end: {sequence_time_end}")
