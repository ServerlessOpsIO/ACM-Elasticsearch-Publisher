'''Write event data to elasticsearch'''

import logging
import json
import os

from elasticsearch import Elasticsearch

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))  # type: ignore
_logger = logging.getLogger(__name__)

ES_HOST = os.environ.get('ES_HOST')
ES_PORT = int(os.environ.get('ES_PORT'))
ES_USERNAME = os.environ.get('ES_USERNAME')
ES_PASSWORD = os.environ.get('ES_PASSWORD')
ES_INDEX = os.environ.get('ES_INDEX')
ES_DOC_TYPE = os.environ.get('ES_DOC_TYPE')

ES = Elasticsearch([ES_HOST],
                   http_auth=(ES_USERNAME, ES_PASSWORD),
)


def _get_message_from_event(event: dict) -> dict:
    '''Get SNS message from event'''
    return json.loads(event.get('Records')[0].get('Sns').get('Message'))


def _publish_to_elastic(item: dict):
    '''Publish an item to ES'''
    resp = ES.index(index=ES_INDEX, doc_type=ES_DOC_TYPE, id=item.get('identity').get('LineItemId'), body=item)
    return resp


def handler(event, context):
    '''Lambda entry point.'''
    _logger.debug('Event received: {}'.format(json.dumps(event)))

    line_item = _get_message_from_event(event)
    publish_resp = _publish_to_elastic(line_item)

    resp = {'elasticsearch': publish_resp}
    _logger.debug('Response: {}'.format(json.dumps(resp)))
    return resp

