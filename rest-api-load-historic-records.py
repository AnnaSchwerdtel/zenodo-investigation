import requests
from datetime import datetime, timezone
import logging
import time
import json


BASE_URL = "https://zenodo.org"
FILE_NAME = "./investigations/zenodo-api/hits_unique_historic.json"


page = 1 
query = 'created:[2015-01-01 TO 2017-10-22]'
hits = []
max_hits = 10_000 # Cannot be bigger than 10k, otherwise API error.
start_time = datetime(2022, 5, 1, tzinfo=timezone.utc)

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s - %(message)s')
logging.Formatter.converter = time.gmtime

while len(hits) < max_hits:
    logging.info(f"Loading page #{page}")
    params = {
        'q': query,
        'size': 1000,
        'sort': 'mostrecent',
        'all_versions': 'false',
        'page': page,
        'type': 'dataset'
    }

    r = requests.get(BASE_URL + "/api/records/", params=params)

    limit = int(r.headers['X-RateLimit-Limit'])
    remaining = int(r.headers['X-RateLimit-Remaining'])
    reset_time_utc = datetime.utcfromtimestamp(int(r.headers['X-RateLimit-Reset']))

    new_hits = r.json()['hits']['hits']
    hits += new_hits

    last_loaded_timestamp = new_hits[-1]['updated']
    last_loaded_timestamp = datetime.strptime(last_loaded_timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')

    total_hits = int(r.json()['hits']['total'])
    max_hits = total_hits if total_hits < max_hits else max_hits

    logging.info(f"Limit: {limit}")
    logging.info(f"Total records to load: {total_hits}")
    logging.info(f"Loaded records: {len(hits)}")
    logging.info(f"Remaining: {remaining}")
    logging.info(f"Reset (UTC): {reset_time_utc}")
    logging.info(f"Current Time (UTC): {datetime.now(timezone.utc)}")
    logging.info(f"Last loaded timestamp (UTC): {last_loaded_timestamp}")


    if remaining == 0:
        current_time = datetime.now(timezone.utc)
        time_to_wait_in_seconds = (reset_time_utc - current_time).total_seconds()
        logging.info(f"Waiting for {time_to_wait_in_seconds} seconds")
        time.sleep(time_to_wait_in_seconds)

    page += 1

logging.info(f"Loaded {len(hits)} entries.")

with open(FILE_NAME, 'w') as file:
    for hit in hits:
        file.write(f"{json.dumps(hit)}\n")

logging.info(f"Stored resutls in file '{FILE_NAME}'")