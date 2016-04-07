"""
thumbp -- Thumbnail Proxy
"""

from flask import Flask, Response, stream_with_context, abort
import logging
import requests
import re

app = Flask(__name__)
es_base = None
valid_id_pat = re.compile(r'^[a-f0-9]{32}$')

@app.route('/thumb/<item_id>', methods=['GET'])  # HEAD will work
def thumb(item_id):
    """
    Return the thumbnail for the given DPLA Item ID

    See http://flask.pocoo.org/snippets/118/ re use of stream_with_context
    """
    item_id = valid_id(item_id)
    
    try:
        es_res = elasticsearch_result(item_id)
        url = es_res.json()['hits']['hits'][0]['_source']['object']
    except KeyError:
        app.logger.error("%s does not have 'object' property" % item_id)
        abort(404)
    except IndexError:
        app.logger.error("Item %s not found" % item_id)
        abort(404)
    except Exception as e:
        app.logger.error("could not complete Elasticsearch query: %s" % e)
        abort(500)

    app.logger.debug("getting %s" % url)
    try:
        resp = image_response_stream(url)
        if resp.status_code == 200:
            return Response(stream_with_context(resp.iter_content()),
                            content_type=resp.headers['content-type'])
        else:
            # `requests' will follow a redirect and give a 200 if it leads to
            # a success.  Consider anything but a 200 to be Not Found for our
            # purposes.
            app.logger.error("HTTP %d for %s" % (req.status_code, url))
            abort(404)
    except Exception as e:
        app.logger.error("could not get %s: %s" % (url, e))

def elasticsearch_result(item_id):
    query_url = es_base + "/_search?q=id:%s" % item_id
    app.logger.debug("query_url: %s" % query_url)
    return requests.get(query_url)

def image_response_stream(url):
    return requests.get(url, stream=True)

def valid_id(item_id):
    """
    Return the given item ID string or abort with a 403 error if it's not valid
    """
    if valid_id_pat.search(item_id):
        return item_id
    else:
        abort(403)

if __name__ == '__main__':
    app.run()
