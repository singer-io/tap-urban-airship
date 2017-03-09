#!/usr/bin/env python3

import datetime
import sys

import requests
import singer

from . import utils
from .transform import transform_row


BASE_URL = "https://go.urbanairship.com/api/"
CONFIG = {
    'app_key': None,
    'app_secret': None,
    'start_date': None,
}
STATE = {}

logger = singer.get_logger()
session = requests.Session()


def get_start(entity):
    if entity not in STATE:
        STATE[entity] = CONFIG['start_date']

    return STATE[entity]


class APIException(Exception):
    def __init__(self, response):
        super(Exception, self).__init__("API returned {error_code}: {error}\n\t{details}".format(**response))


def gen_request(endpoint):
    auth = requests.auth.HTTPBasicAuth(CONFIG['app_key'], CONFIG['app_secret'])
    headers = {'Accept': "application/vnd.urbanairship+json; version=3;"}
    if 'user_agent' in CONFIG:
        headers['User-Agent'] = CONFIG['user_agent']

    url = BASE_URL + endpoint
    while url:
        req = requests.Request('GET', url, auth=auth, headers=headers).prepare()
        logger.info("GET {}".format(req.url))
        resp = session.send(req)
        if resp.status_code >= 400:
            try:
                data = resp.json()
                logger.error("GET {0} [{1.status_code} - {error} ({error_code})]".format(req.url, resp, **data))
            except:
                logger.error("GET {0} [{1.status_code} - {1.content}]".format(req.url, resp))

            sys.exit(1)

        data = resp.json()
        for row in data[endpoint]:
            yield row

        url = data.get('next_page')


def sync_entity(entity, primary_keys, date_keys=None, transform=None):
    schema = utils.load_schema(entity)
    singer.write_schema(entity, schema, primary_keys)

    start_date = get_start(entity)
    for row in gen_request(entity):
        if transform:
            row = transform(row)

        row = transform_row(row)
        if date_keys:
            last_touched = max(row[date_key] for date_key in date_keys)
            utils.update_state(STATE, entity, last_touched)
            if last_touched < start_date:
                continue

        singer.write_record(entity, row)

    singer.write_state(STATE)


def do_sync():
    logger.info("Starting sync")

    # Lists, Channels, and Segments are very straight forward to sync. They
    # each have two dates that need to be examined to determine the last time
    # the record was touched.
    sync_entity("lists", ["name"], ["created", "last_updated"])
    sync_entity("channels", ["channel_id"], ["created", "last_registration"])
    sync_entity("segments", ["id"], ["creation_date", "modificiation_date"])

    # Named Users have full channel objects nested in them. We only need the
    # ids for generating the join table, so we transform the list of channel
    # objects into a list of channel ids before transforming the row based on
    # the schema.
    def flatten_channels(item):
        item['channels'] = [c['channel_id'] for c in item['channels']]
        return item

    sync_entity("named_users", ["named_user_id"], transform=flatten_channels)

    logger.info("Sync completed")


def main():
    args = utils.parse_args()

    config = utils.load_json(args.config)
    utils.check_config(config, ["app_key", "app_secret", "start_date"])
    CONFIG.update(config)

    if args.state:
        STATE.update(utils.load_json(args.state))

    do_sync()


if __name__ == '__main__':
    main()
