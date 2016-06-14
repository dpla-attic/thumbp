'use strict';

const http = require('http');
const libRequest = require('request');
const cluster = require('cluster');
const numCPUs = require('os').cpus().length;

const path_pat = /^\/thumb\/([a-f0-9]{32})$/;
const es_base = process.argv[2] || 'http://localhost:9200/dpla_alias/item';
const port = process.argv[3] || '8080';


/***
 * thumbp:  DPLA Thumbnail Image Proxy
 * -----------------------------------
 *
 * Example invocation:
 * $ node thumbp.js http://my-es-server:9200/dpla_alias/item 8080
 *
 */

/*
 * Connection
 * ---
 * The connection between `thumbp' server and its client, with a request and
 * a response.
 */
function Connection(request, response) {
    this.request = request;
    this.response = response;
    this.response.setHeader('Server', 'DPLA thumbp');
    this.request.on('data', () => {
        return; // noop
    }).on('error', (e) => {
        console.error(e);
        this.returnError(500);
    }).on('end', () => {
        this.handleReqEnd();
    });
    this.imageURL = null;
    this.itemID = null;
}

exports.Connection = Connection;  // Exported for the sake of our tests


/*
 * Handle the /thumb request 'end' event, when the request is complete.
 */
Connection.prototype.handleReqEnd = function() {
    if (this.request.method === 'GET') {
        var match_result = path_pat.exec(this.request.url);
        if (match_result !== null) {
            this.itemID = match_result[1];
            this.lookUpImage();
        } else {
            this.returnError(400);
        }
    } else {
        this.returnError(405);
    }
};


/*
 * Given an item ID, look up the image URL and proxy it.
 */
Connection.prototype.lookUpImage = function() {
    var q_url = es_base + `/_search?q=id:${this.itemID}&fields=id,object`;
    libRequest(q_url, (error, response, body) => {
        this.checkSearchResponse(error, response, body);
    });
};


/*
 * Check the response from the Elasticsearch query request, and proceed
 * to proxying the image if it's OK.
 */
Connection.prototype.checkSearchResponse = function(error, response, body) {
    if (!error && response.statusCode == 200) {
        try {
            var item_data = JSON.parse(body);
            if (item_data['hits']['total'] == 0) {
                this.returnError(404);
                return;
            }
            var url = item_data['hits']['hits'][0]['fields']['object'];
            if (url) {
                this.imageURL = url;
                this.proxyImage();
            } else {
                console.error(`no object property for item ${this.itemID}`);
                this.returnError(404);
            }
        } catch (e) {
            console.error(e.stack);
            this.returnError(500);
        }
    } else {
        console.error(error);
        this.returnError(500);
    }
};

/*
 * Given an image URL, pipe the image to the client response.
 *
 * The `request' response (i.e. the response of what we're namespacing as
 * `libRequest', which is the response from the provider's image resource)
 * is piped into the response we're sending to our client.
 */
Connection.prototype.proxyImage = function() {
    try {
        libRequest({
            method: 'GET',
            uri: this.imageURL,
            headers: {
                'User-Agent': 'DPLA thumbp (https://github.com/dpla/thumbp)'
            },
            timeout: 4000  // ms
        }).on('response', (response) => {
            this.handleImageResponse(response);
        }).on('error', (error) => {
            this.handleImageConnectionError(error);
        }).pipe(this.response);
    } catch (e) {
        console.error(e.stack);
        this.returnError(500);
    }
};


/*
 * Handle the image request's 'response' event, which allows us to manipulate
 * the response object before it gets piped to the response we send to our
 * client in proxyImage().
 *
 * We customize the return code and response headers.
 */
Connection.prototype.handleImageResponse = function(imgResponse) {
    // Reduce headers to just those that we want to pass through
    var cl = imgResponse.headers['content-length'] || false;
    var ct = imgResponse.headers['content-type'] || false;
    var lm = imgResponse.headers['last-modified'] || false;
    imgResponse.headers = {
        'Date': imgResponse.headers['date'],
    };
    cl && (imgResponse.headers['Content-Length'] = cl);
    ct && (imgResponse.headers['Content-Type'] = ct);
    lm && (imgResponse.headers['Last-Modified'] = lm);

    // We have our own ideas of which response codes are appropriate for our
    // client.
    switch(imgResponse.statusCode) {
        case 200:
            break;
        case 404:
        case 410:
            // We treat a 410 as a 404, because our provider could correct
            // the `object' property in the item's metadata, meaning the
            // resource doesn't have to be "410 Gone".
            console.error(`${this.imageURL} not found`);
            imgResponse.statusCode = 404;
            break;
        default:
            // Other kinds of errors are just considered "bad gateway" errors
            // because we don't want to own them.
            console.error(
                `${this.imageURL} status ${imgResponse.statusCode}`
            );
            imgResponse.statusCode = 502;
            break;
    }
};


/*
 * Handle errors with the HTTP connection to the image webserver.
 */
Connection.prototype.handleImageConnectionError = function(error) {
    console.error(error);
    if (error.code === 'ETIMEDOUT') {
        this.returnError(504);
    } else {
        this.returnError(502);
    }
};


Connection.prototype.returnError = function(code) {
    this.response.statusCode = code;
    this.response.end();
};


if (require.main === module) {

    process.on('uncaughtException', (err) => {
        console.error('Uncaught exception: ', err.stack);
    });


    if (cluster.isMaster) {
        // Fork workers, 1 for each CPU.
        cluster.on('exit', (worker, code, signal) => {
            console.log(`worker ${worker.process.pid} died`);
        }).on('online', (worker) => {
            console.log(`worker ${worker.process.pid} online`);
        });
        for (var i = 0; i < numCPUs; i++) {
            cluster.fork();
        }
    } else {
        // Worker: create a server and handle each request with a Connection.
        http.createServer(function(request, response) {
            new Connection(request, response);
        }).listen(port);
    }

}
