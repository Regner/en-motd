

import os
import json
import logging
import requests

from time import sleep
from gcloud import datastore, pubsub

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# App Settings
SLEEP_TIME = int(os.environ.get('SLEEP_TIME', 30))
EN_TOPIC_SETTINGS = os.environ.get('EN_TOPIC_SETTINGS', 'http://en-topic-settings:80/external')

# Datastore Settings
DS_CLIENT = datastore.Client()
SERVICE_KIND = 'EN-MOTD'

# PubSub Settings
PS_CLIENT = pubsub.Client()
PS_TOPIC = PS_CLIENT.topic(os.environ.get('NOTIFICATION_TOPIC', 'send_notification'))

if not PS_TOPIC.exists():
    PS_TOPIC.create()


def send_notification(title, subtitle, topic):
    topics = json.dumps([topic])
    
    PS_TOPIC.publish(
        '',
        title=title,
        subtitle=subtitle,
        service='en-motd',
        topics=topics,
    )


def get_services():
    response = requests.get(EN_TOPIC_SETTINGS)
    response.raise_for_status()

    return response.json()['motd']['topics']


def update_latest_entry(motd, latest_id, new_latest_id):
    if latest_id is None:
        latest_id = datastore.Entity(DS_CLIENT.key(SERVICE_KIND, 'latest-id', 'MOTD', motd))
        latest_id['id'] = new_latest_id
        DS_CLIENT.put(latest_id)

    if latest_id['id'] != new_latest_id:
        latest_id['id'] = new_latest_id
        DS_CLIENT.put(latest_id)
    

while True:
    services = get_services()
    
    for motd in services:
        logger.info('Checking "{}" for updated message.'.format(motd['name']))

        response = requests.get(motd['url'])
        response.raise_for_status()
        
        motd_data = response.json()

        latest_id = DS_CLIENT.get(DS_CLIENT.key(SERVICE_KIND, 'latest-id', 'MOTD', motd['name']))
        
        if latest_id is not None and latest_id['id'] == motd_data['Id']:
            continue

        logger.info('New entry found for "{}"! Entry title: {}'.format(motd['name'], motd_data['Motd']['Title']))
        
        send_notification(motd['name'], motd_data['Motd']['Title'], motd['topic'])
        update_latest_entry(motd['name'], latest_id, motd_data['Id'])

    sleep(SLEEP_TIME)
