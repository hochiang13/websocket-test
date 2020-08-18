#!/usr/bin/env python
from flask import Flask, session, request, g, current_app
from flask_socketio import SocketIO, emit, disconnect
import requests, json
from base64 import b64encode
import time
import os
import websocket, ssl, base64


async_mode = "eventlet"
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY") or \
    'cannot be guessed'
app.config["RANCHER_IP"] = os.environ.get("RANCHER_IP") or \
    "10.134.202.115"
socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*")


@socketio.on('connect', namespace='/shell')
def shell_connect():
    # note: the connect event on server side must end,
    # or the server will not accept events!

    print("Connect event.")
    token = request.headers.get("Authorization")
    cluster_id = request.headers.get("clusterid")
    namespace = request.args.get("namespace")
    pod = request.args.get("pod")
    for key in token, cluster_id, namespace, pod:
        if not isinstance(key, str):
            print("connect event, missing data from frontend.")
            return False
        if len(key) == 0:
            print("connect event, missing data from frontend.")
            return False
    if len(token.split(" ")) != 2:
        print("connect event, unexpected Authorization received.")
        return False
    if token.split(" ")[0] != "Bearer":
        print("connect event, unexpected Authorization received.")
        return False

@socketio.on('first_event', namespace='/shell')
def shell_first():
    # need a first event after connect event to start websocket to rancher.
    # Tried starting a background thread in the connect event function,
    #   it doesn't work because it is outside of the application context,
    #   and socketio.emit will send event to all clients.

    print("first_event.")
    token = request.headers.get("Authorization")
    cluster_id = request.headers.get("clusterid")
    namespace = request.args.get("namespace")
    pod = request.args.get("pod")
    # if container is not included as a parameter in the websocket connect http request,
    #   automatically choose the first container of the pod.
    container = request.args.get("container")

    #container=k8s-ws&
    url = f"wss://{current_app.config['RANCHER_IP']}/k8s/clusters/{cluster_id}/api/v1"
    url += f"/namespaces/{namespace}/pods/{pod}/exec?"
    if isinstance(container, str):
        url += f"container={container}&"
    url += "stdout=1&stdin=1&stderr=1&tty=1"
    url += "&command=%2Fbin%2Fsh&command=-c&command=TERM%3Dxterm-256color%3B%20export%20"
    url += "TERM%3B%20%5B%20-x%20%2Fbin%2Fbash%20%5D%20%26%26%20(%5B%20-x%20%2Fusr%2Fbin"
    url += "%2Fscript%20%5D%20%26%26%20%2Fusr%2Fbin%2F"
    url += "script%20-q%20-c%20%22%2Fbin%2Fbash%22%20%2F"
    url += "dev%2Fnull%20%7C%7C%20exec%20%2Fbin%2Fbash)%20%7C%7C%20exec%20%2Fbin%2Fsh"

    try:
        session["wss"] = websocket.create_connection(
            url,
                sslopt={"cert_reqs": ssl.CERT_NONE},
                header={"Authorization": token},
                subprotocols=['base64.channel.k8s.io']
            )
    except Exception as e:
        print(f"create_connection exception: {e}")
        disconnect()
        return
    while True:
        try:
            temp_string = session["wss"].recv()
        except Exception as e:
            print(f"wss recv exception: {e}")
            break
        #return_string = base64.b64decode(temp_string[1:].encode()).decode()
        print(f"sending string to browser: {temp_string}")
        emit("server_response", temp_string)
    disconnect()

@socketio.on('submit_event', namespace='/shell')
def shell_submit(message):
    print(f"submit_event, message: {message}")
    if message:
        #temp_string = "0" + (base64.b64encode(message.encode())).decode()
        print(f"sending to rancher: {message}")
        try:
            session["wss"].send(message)
        except Exception as e:
            print(f"wss send exception: {e}")

@socketio.on('disconnect', namespace='/shell')
def shell_disconnect():
    print('Client disconnected', request.sid)
    try:
        session["wss"].close()
    except Exception as e:
        print(f"disconnect exception: {e}")

@socketio.on('connect', namespace='/log')
def log_connect():
    # note: the connect event on server side must end,
    # or the server will not accept events!

    print("Connect event.")
    token = request.headers.get("Authorization")
    cluster_id = request.headers.get("clusterid")
    namespace = request.args.get("namespace")
    pod = request.args.get("pod")
    for key in token, cluster_id, namespace, pod:
        if not isinstance(key, str):
            print("connect event, missing data from frontend.")
            return False
        if len(key) == 0:
            print("connect event, missing data from frontend.")
            return False
    if len(token.split(" ")) != 2:
        print("connect event, unexpected Authorization received.")
        return False
    if token.split(" ")[0] != "Bearer":
        print("connect event, unexpected Authorization received.")
        return False

@socketio.on('first_event', namespace='/log')
def log_first():
    # need a first event after connect event to start websocket to rancher.
    # Tried starting a background thread in the connect event function,
    #   it doesn't work because it is outside of the application context,
    #   and socketio.emit will send event to all clients.

    print("first_event.")
    token = request.headers.get("Authorization")
    cluster_id = request.headers.get("clusterid")
    namespace = request.args.get("namespace")
    pod = request.args.get("pod")
    # if container is not included as a parameter in the websocket connect http request,
    #   automatically choose the first container of the pod.
    container = request.args.get("container")

    url = f"wss://{current_app.config['RANCHER_IP']}/k8s/clusters/{cluster_id}/api/v1/"
    url += f"namespaces/{namespace}/pods/{pod}/log?"
    if isinstance(container, str):
        url += f"container={container}&"
    url += "tailLines=500&follow=true&timestamps=true&previous=false"
    try:
        session["wss"] = websocket.create_connection(
            url,
                sslopt={"cert_reqs": ssl.CERT_NONE},
                header={"Authorization": token},
                subprotocols=['base64.binary.k8s.io']
            )
    except Exception as e:
        print(f"create_connection exception: {e}")
        disconnect()
        return
    while True:
        try:
            temp_string = session["wss"].recv()
        except Exception as e:
            print(f"wss recv exception: {e}")
            break
        print(f"sending string to browser: {temp_string}")
        emit("server_response", temp_string)
    disconnect()

@socketio.on('disconnect', namespace='/log')
def log_disconnect():
    print('Client disconnected', request.sid)
    try:
        session["wss"].close()
    except Exception as e:
        print(f"disconnect exception: {e}")


if __name__ == '__main__':
    socketio.run(app, debug=False)

