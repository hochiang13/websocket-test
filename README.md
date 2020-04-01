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

Kubernetes notes
----------------

The flask web server connects to Kubernetes api server to run shell commands in containers.

Kubernetes client python library on github:
```
https://github.com/kubernetes-client/python
```

Flask socketio documents:
```
https://flask-socketio.readthedocs.io/en/latest/
```

