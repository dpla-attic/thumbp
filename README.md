# thumbp

## Setting up with pyenv

1. Install pyenv.  Install Python 3.5.1.
2. Change into the directory containing this project
2. `pip install -r requirements.txt`
3. `./thumbp_server -h`

## Setting up with virtualenv

1. Install pyenv and Python 3.5.1 as above
2. `virtualenv thumbp`  (Creates a virtualenv directory tree)
3. `cd thumbp`
4. `. bin/activate`
5. `mkdir src`
6. Check out or otherwise copy this project's directory into its own directory
   under src.
7. `cd` to the project directory and do steps 2 and 3 of "Setting up with pyenv"
   above.

## Installing for development or testing

```
pip install -e .[testing]
py.test -v
```

## Example invocation

```
$ ./gevent_wsgi.py -e http://my-es-server:9200/dpla_alias -l app.log \
   -f thumbp.pid
```

Example thumbnail given that invocation:
`http://localhost:8080/thumb/aacca3079a48aaacc3cdb473379048fc`

## Why Gevent + Flask + Python?

1. I've used gevent before and can get this up and running quickly
2. I'd rather not tie this in with the frontend or API apps for various reasons.
3. It's event-based (like NGINX) and handles concurrent requests well.
4. It's small memory-wise (~ 23 MB in my experience) and code-wise.

## TODO

* Try to get back from Elasticsearch only the field we need instead of the
  whole document.
* Get server to detach when it runs and log to a provided file instead of
  stderr. (See WSGIServer re logging.)
* We may want to pass through more headers, like Last-Modified, although this
  is intended to run behind a reverse proxy like NGINX with aggressive caching
  being forced.
* We may want to observe If-Modified-Since and pass back 304 responses from
  the upstream to the client.


