# thumbp

## Setting up with pyenv

1. Install pyenv.  Install Python 2.7.10.
2. Change into the directory containing this project
3. `pip install -r requirements.txt`

## Setting up with virtualenv

1. Install pyenv and Python 2.7.10 as above
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

This runs the application in a `twistd` webserver without detaching from your
console:
```
$ ES_BASE=http://es-loadbal:9200/dpla_alias/item twistd -n web \
  --class=thumbp.thumbp.resource
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


