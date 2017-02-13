#!/usr/bin/env python3

import argparse
import datetime
import json
import os

import requests
import stitchstream


BASE_URL = "https://go.urbanairship.com/api/"
APP_KEY = None
APP_SECRET = None
DATETIME_FMT = "%Y-%m-%dT%H:%M:%SZ"
DEFAULT_START_DATE = datetime.datetime.utcnow() - datetime.timedelta(years=1)

state = {}
logger = stitchstream.get_logger()


class APIException(Exception):
    def __init__(self, response):
        super(Exception, self).__init__("API returned an error\n"
                                        "{error_code}: {error}\n"
                                        "{details}"
                                        .format(**response))


def load_schema(entity):
    path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "tap_urban_airship",
        "{}.json".format(entity))

    with open(path) as f:
        return json.load(f)


def update_state(entity, dt):
    if dt is None:
        return

    if isinstance(dt, datetime):
        dt = dt.strftime(DATETIME_FMT)

    if dt > state[entity]:
        state[entity] = dt


def request(url, params=None):
    params = params or {}
    response = requests.get(url, params=params, auth=(APP_KEY, APP_SECRET))
    response.raise_for_status()
    return response


def sync_entity(entity, primary_keys, date_keys=None, transform=None):
    schema = load_schema(entity)
    stitchstream.write_schema(entity, schema, primary_keys)

    start = state.get(entity, DEFAULT_START_DATE)
    url = BASE_URL + entity
    while url:
        resp = request(url)
        data = resp.json()

        if not data['ok']:
            raise APIException(data)

        for row in data[entity]:
            if transform:
                row = transform(row)

            transformed = transform_row(row)
            if date_keys:
                last_touched = max(transformed[date_key] for date_key in date_keys)
                if last_touched > start:
                    update_state(entity, last_touched)
                    stitchstream.write_record(entity, transformed)

            else:
                stitchstream.write_record(entity, transformed)

        stitchstream.write_state(state)


def flatten_channels(item):
    item['channels'] = [c['channel_id'] for c in item['channels']]
    return item


def do_sync():
    sync_entity("lists", ["name"], ["created", "last_updated"])
    sync_entity("channels", ["channel_id"], ["created", "last_registration"])
    sync_entity("segments", ["id"], ["creation_date", "modificiation_date"])
    sync_entity("named_users", ["named_user_id"], transform=flatten_channels)


def main():
    global APP_KEY
    global APP_SECRET

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Config file', required=True)
    parser.add_argument('-s', '--state', help='State file')
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    APP_KEY = config['app_key']
    APP_SECRET = config['app_secret']

    if args.state:
        logger.info("Loading state from " + args.state)
        with open(args.state) as f:
            state.update(json.load(f))

    do_sync()


if __name__ == '__main__':
    main()
