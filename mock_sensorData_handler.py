#!/usr/bin/env python

# Copyright 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import gzip
import logging
import os
import argparse
import datetime
import subprocess
from google.cloud import pubsub, storage

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
stage = os.environ.get('stage', 'dev')
TOPIC = 'sensorData'
BUCKET = 'cloud-training-demos'
FILENAME = 'sandiego/sensor_obs2008.csv.gz'
INPUT = '/tmp/export_sensor_obs2008.csv.gz'


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print('Blob {} downloaded to {}.'.format(
        source_blob_name,
        destination_file_name))


download_blob(BUCKET, FILENAME, INPUT)



def publish(publisher, topic, events):
   numobs = len(events)
   if numobs > 0:
       logging.info('Publishing {0} events from {1}'.format(numobs, get_timestamp(events[0])))
       for event_data in events:
         publisher.publish(topic,event_data)

def get_timestamp(line):
   ## convert from bytes to str
   line = line.decode('utf-8')

   # look at first field of row
   timestamp = line.split(',')[0]
   return datetime.datetime.strptime(timestamp, TIME_FORMAT)

def simulate(topic, ifp, firstObsTime, publisher,
             programStart, speedFactor, limit):
   # sleep computation
   def compute_sleep_secs(obs_time):
        time_elapsed = (datetime.datetime.utcnow() - programStart).seconds
        sim_time_elapsed = (obs_time - firstObsTime).seconds / speedFactor
        to_sleep_secs = sim_time_elapsed - time_elapsed
        return to_sleep_secs

   topublish = list() 

   for i, line in enumerate(ifp):
       if i >= limit:
          print("i: {} -- Breaking Loop".format(i))
          break
       event_data = line   # entire line of input CSV is the message
       obs_time = get_timestamp(line) # from first column

       # how much time should we sleep?
       if compute_sleep_secs(obs_time) > 1:
          # notify the accumulated topublish
          publish(publisher, topic, topublish) # notify accumulated messages
          topublish = list() # empty out list

          # recompute sleep, since notification takes a while
          to_sleep_secs = compute_sleep_secs(obs_time)
          if to_sleep_secs > 0:
             logging.info('Sleeping {} seconds'.format(to_sleep_secs))
             time.sleep(to_sleep_secs)
       topublish.append(event_data)

   # left-over records; notify again
   publish(publisher, topic, topublish)
   response = "Completed {} events".format(i)
   print(response)
   return response

def peek_timestamp(ifp):
   # peek ahead to next line, get timestamp and go back
   pos = ifp.tell()
   line = ifp.readline()
   ifp.seek(pos)
   return get_timestamp(line)


def main(event):

    print("Event: {}".format(event))
    
    event = event.get_json(silent=True)
    speedFactor = event.get("speedFactor", 60)
    project = os.environ.get('GCP_PROJECT', 'UNKNOWN')
    limit = event.get("limit", 3)
    print("speedFactor: {}  project: {}  limit: {}".format(speedFactor,
                                                           project,
                                                           limit))

    if stage == 'prod':
        error = "Cannot run simulations in Production Env!!"
        print(error)
        raise Exception + error

    # create Pub/Sub notification topic
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.INFO)
    publisher = pubsub.PublisherClient()
    topic = "{}_{}".format(TOPIC, stage)
    event_type = publisher.topic_path(project, topic)
    try:
        publisher.get_topic(event_type)
        logging.info('Reusing pub/sub topic {}'.format(topic))
    except Exception:
        publisher.create_topic(event_type)
        logging.info('Creating pub/sub topic {}'.format(topic))

    # notify about each line in the input file
    programStartTime = datetime.datetime.utcnow()
    with gzip.open(INPUT, 'rb') as ifp:
        ifp.readline()  # skip header
        firstObsTime = peek_timestamp(ifp)
        logging.info('Sending sensor data from {}'.format(firstObsTime))
        response = simulate(event_type,
                             ifp,
                             firstObsTime,
                             publisher,
                             programStartTime,
                             speedFactor,
                             limit)

    return response