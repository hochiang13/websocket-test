#!/usr/bin/env python
from flask import Flask, session, request, g, current_app
from flask_socketio import SocketIO, emit, disconnect
import requests, json
from base64 import b64encode
from kubernetes.config.kube_config import KubeConfigLoader
from kubernetes.client import Configuration
from kubernetes.client.rest import ApiException
from kubernetes.client.api import core_v1_api
from kubernetes.stream import stream

async_mode = "eventlet"


app = Flask(__name__)
app.config['SECRET_KEY'] = 'cannot be guessed'
app.config["ADMIN_TOKEN"] = "token-hxfsx:kqdf44kck5n4pdnjs4v22hchlvdb95g59xt5nmj75ldsgx2wnq695f"
app.config["RANCHER_IP"] = "10.62.164.163"
socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*")

# request rancher for cacert, base64 encode it, and save string for kubernetes_config.py
url = "https://{0}/v3/settings/cacerts".format(app.config["RANCHER_IP"])
querystring = {}
payload = {}
headers = {
    'Authorization': app.config["ADMIN_TOKEN"],
    'Content-Type': "application/json"
}
try:
    response = requests.get(
        url, data=json.dumps(payload), headers=headers, params=querystring,
        verify=False)
except:
    print("Cannot connect to rancher server for cacert, abort!")

response_json = json.loads(response.text)
if response.status_code != 200:
    print("GET cacert reply " + response.status_code + ", abort!")

app.config["CACERT"] = b64encode(response_json["value"].encode("utf-8")).decode("utf-8")


def load_kubernetes_config(token, cluster_id):
    # CACERT read from rancher, set token to ADMIN_TOKEN for now
    #token = token.split(" ")[1]
    dummy_string = "dummy"
    token = current_app.config["ADMIN_TOKEN"].split(" ")[1]
    server_string = "https://" + current_app.config["RANCHER_IP"]
    server_string += "/k8s/clusters/"
    server_string += cluster_id
    dictionary = {
        "current-context": dummy_string,
        "contexts": [
            {
                "name": dummy_string,
                "context": {
                    "user": dummy_string,
                    "cluster": dummy_string
                }
            }
        ],
        "clusters": [
            {
                "name": dummy_string,
                "cluster": {
                    "server": server_string,
                    "certificate-authority-data": current_app.config["CACERT"]
                }
            }
        ],
        "users": [
            {
                "name": dummy_string,
                "user": {
                    "token": token
                }
            }
        ]
    }
    loader = KubeConfigLoader(config_dict=dictionary)
    c = type.__call__(Configuration)
    loader.load_and_set(c)
    Configuration.set_default(c)


@socketio.on('connect', namespace='/test')
def test_connect():
    print("server connect event, sending server_response.")
    emit('server_response', {'data': 'Connected', 'count': 0})

@socketio.on('first_event', namespace='/test')
def first_message(message):
    print("server first_event, data: " + str(message.get("data")))
    """
    session["cluster_id"] = message["cluster_id"]
    session["token"] = message["token"]
    """

@socketio.on('submit_event', namespace='/test')
def test_message(message):
    print("server submit_event, sending server_resonse.")
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('server_response',
         {'data': message['data'], 'count': session['receive_count']})

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)



@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')


if __name__ == '__main__':
    socketio.run(app, debug=True)

