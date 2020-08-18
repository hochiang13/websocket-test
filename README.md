Poseidon websocket server
=========================

A flask websocket server that acts as a go-between for xterm javascript module as the client on the browser, and the exec and log websocket server on rancher.

Run browser client
--------------

Serve html/index.html with a nginx container.

```
docker run -d --name nginx_wd -p 80:80 -v /<full_local_path>/html/:/usr/share/nginx/html/ nginx:alpine
```

Open html on browser with the following URLs:
```
http://192.168.56.101
http://192.168.56.101/log.html
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

Create docker container for flask server
----------------------------------
```
docker build -t 10.134.200.110:5000/k8s-ws:version .
```

Flask server notes
------------------

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

When running on production and flask server needs to be scaled up -- each websocket connection needs to send all its data to the same flask server container, so make sure enable session affinity for the loadbalancer service to nginx ingress controller, and set the following annotation for the websocket ingress:
```
nginx.ingress.kubernetes.io/affinity = cookie
```

xterm javascript library
------------------------

To use index.html with xterm, the xterm javascript library has to be installed with the following command:
```
npm install xterm
```
And then move the entire node_modules/ directory into /html/.

Use the following addon to fit the text output to the terminal object:
```
https://github.com/xtermjs/xterm.js/tree/master/addons/xterm-addon-fit
```
Note: cannot get this to work on the test index.html, import doesn't work for html embedded javascript.

