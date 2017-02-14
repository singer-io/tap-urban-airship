#!/usr/bin/env python3

import datetime

import requests
import singer

from . import utils
from .transform import transform_row


CONFIG = {
    'base_url': "https://go.urbanairship.com/api/",
    'default_start_date': utils.strftime(datetime.datetime.utcnow() - datetime.timedelta(days=365)),

    # in config.json
    'app_key': None,
    'app_secret': None,
}
STATE = {}

logger = singer.get_logger()


class APIException(Exception):
    def __init__(self, response):
        super(Exception, self).__init__("API returned {error_code}: {error}\n\t{details}".format(**response))


def gen_request(endpoint):
    auth = (CONFIG['app_key'], CONFIG['app_secret'])
    url = CONFIG['base_url'] + endpoint
    while url:
        resp = requests.get(url, params=params, auth=auth)
        resp.raise_for_status()

        data = resp.json()
        if not data['ok']:
            raise APIException(data)

        for row in data[entity]:
            yield row

        url = data.get('next_page')


def sync_entity(entity, primary_keys, date_keys=None, transform=None):
    schema = utils.load_schema(entity)
    singer.write_schema(entity, schema, primary_keys)

    start_date = STATE.get(entity, CONFIG['default_start_date'])
    for row in gen_request(entity):
        if transform:
            row = transform(row)

        transformed = transform_row(row)
        if date_keys:
            last_touched = max(transformed[date_key] for date_key in date_keys)
            utils.update_state(STATE, entity, last_touched)
            if last_touched < start_date:
                continue

        singer.write_record(entity, transformed)

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
    CONFIG.update(utils.load_json(args.config))
    if args.state:
        STATE.update(utils.load_json(args.state))
    do_sync()


if __name__ == '__main__':
    main()
