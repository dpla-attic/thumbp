# thumbp

## Setting up with `npm`

This will install packages locally into `node_modules` within `thumbp`:

```
$ cd /path/to/thumbp/dir
$ npm install
```


## Installing for development or testing

```
$ npm install -g mocha
$ mocha
```

## Example invocation

This runs the application locally on port 8080 without detaching from your
console:
```
$ node thumbp.js http://es_loadbal:9200/dpla_alias/item 8080
```

Example thumbnail given that invocation:
`http://localhost:8080/thumb/aacca3079a48aaacc3cdb473379048fc`


## TODO

* Improve logging
* We may want to pass through more headers, like Last-Modified, although this
  is intended to run behind a reverse proxy like NGINX with aggressive caching
  being forced.
* We may want to observe If-Modified-Since and pass back 304 responses from
  the upstream to the client.
