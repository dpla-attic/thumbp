"""
thumbp -- Thumbnail Proxy
"""

from .errors import NotFound, ServerError, Forbidden, GatewayTimeout
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.python import log
from os import environ
from klein import Klein
import treq
import requests
import logging
import re

app = Klein()
resource = app.resource
es_base = environ.get('ES_BASE') or 'http://localhost:9200/dpla_alias/item'
valid_id_pat = re.compile(r'^[a-f0-9]{32}$')


@app.route('/thumb/<item_id>', methods=['GET'])  # HEAD will work
@inlineCallbacks
def thumb(request, item_id):
    """Return the thumbnail for the given DPLA Item ID"""
    # I would prefer not to use inlineCallbacks and use deferreds explicitly,
    # because that would make it easier to chain a couple of deferreds
    # together in order to have the Elasticsearch request not block, and have
    # the image request chain after it.  The problem, though, is that I can't
    # figure out how to set the necessary Content-Type header without using
    # the inlineCallbacks method.  -- Mark B
    item_id = valid_id(item_id)

    try:
        es_res = elasticsearch_result(item_id)
        url = es_res.json()['hits']['hits'][0]['fields']['object']
    except KeyError:
        log.msg("%s does not have 'object' property" % item_id,
                logLevel=logging.ERROR)
        raise NotFound()
    except IndexError:
        log.msg("Item %s not found" % item_id, logLevel=logging.ERROR)
        raise NotFound()
    except Exception as e:
        log.msg("could not complete Elasticsearch query: %s" % e,
                logLevel=logging.ERROR)
        raise ServerError()

    log.msg("getting %s" % url, logLevel=logging.DEBUG)
    try:
        deferred = yield treq.get(url, timeout=4)
        content = yield deferred.content()
        content_type = deferred.headers.getRawHeaders('Content-Type')[0]
        request.setHeader('Content-Type', content_type)
        returnValue(content)
    except Exception as e:
        log.msg("could not get %s: %s" % (url, e), logLevel=logging.ERROR)
        raise ServerError()


def elasticsearch_result(item_id):
    # FIXME: this is still synchronous
    query_url = es_base + "/_search?q=id:%s&fields=id,object" % item_id
    log.msg("query_url: %s" % query_url, logLevel=logging.DEBUG)
    return requests.get(query_url)


def valid_id(item_id):
    """Return the given item ID string or abort with a 403 error if it's
    not valid
    """
    if valid_id_pat.search(item_id):
        return item_id
    else:
        raise Forbidden()


@app.handle_errors(NotFound)
def not_found(response, failure):
    response.setResponseCode(404)
    return 'Not Found'


@app.handle_errors(ServerError)
def server_error(response, failure):
    response.setResponseCode(500)
    return 'Server Error'


@app.handle_errors(Forbidden)
def forbidden(response, failure):
    response.setResponseCode(403)
    return 'Forbidden'


@app.handle_errors(GatewayTimeout)
def gateway_timeout(response, failure):
    response.setResponseCode(504)
    return 'Gateway Timeout'


if __name__ == '__main__':
    app.run("localhost", 8080)
