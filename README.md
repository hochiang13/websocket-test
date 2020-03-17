Testing websocket
=================

Test browser javascript websocket client, and Flask websocket server.

Browser client
--------------

Serve html/index.html with a nginx container.

```
docker run -d --name nginx -p 80:80 -v /<full_local_path>/html/:/usr/share/nginx/html/ nginx:alpine
```

Flask server
------------


