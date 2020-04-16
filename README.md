Testing websocket
=================

Test browser javascript websocket client, flask websocket server, and python kubectl library to connect to container shell.

Run browser client
--------------

Serve html/index.html with a nginx container.

```
docker run -d --name nginx_wd -p 80:80 -v /<full_local_path>/html/:/usr/share/nginx/html/ nginx:alpine
```

Run flask server
------------

First, create virtual python environment and install python libraries.
```
python3.6 -m venv venv
source venv/bin/activate
pip install -r  requirements.txt
```

Then, start flask web server (from the directory where app.py is located):
```
gunicorn -b 0.0.0.0:8080 --worker-class eventlet -w 1 app:app
```

websocket notes
---------------

The flask web server connects to rancher exec websocket to run shell commands in containers, using python library websocket-client.

websocket-client documents:
```
https://pypi.org/project/websocket_client/
```

rancher exec websocket client javascript code:
```
https://github.com/rancher/ui/blob/master/lib/shared/addon/components/container-shell/component.js#L80-L150
```

Flask socketio documents:
```
https://flask-socketio.readthedocs.io/en/latest/
```

xterm javascript library
------------------------

To use index.html with xterm, the xterm javascript library has to be installed with the following command:
```
npm install xterm
```
And then move the entire node_modules/ directory into /html/.
