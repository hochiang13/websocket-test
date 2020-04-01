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
    token = token.split(" ")[1]
    dummy_string = "dummy"
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
    print("Connect event.")

@socketio.on('first_event', namespace='/test')
def first_message(message):
    print("first_event, data: " + str(message.get("data")))
    session["cluster_id"] = message.get("cluster_id")
    session["token"] = message.get("Authorization")
    if (
        session["cluster_id"] is None or
        session["token"] is None
    ):
        print("first_event, missing cluster_id and/or token.")
        disconnect()
        return
    load_kubernetes_config(
        token=session["token"],
        cluster_id=session["cluster_id"]
    )
    session["api"] = core_v1_api.CoreV1Api()
    exec_command = ['/bin/sh']
    session["resp"] = stream(
        session["api"].connect_get_namespaced_pod_exec,
        name="efk-kibana-5dc5c455df-bk776",
        namespace='efk',
        command=exec_command,
        stderr=True, stdin=True,
        stdout=True, tty=False,
        _preload_content=False
    )
    while session["resp"].is_open():
        session["resp"].update(timeout=1)
        if session["resp"].peek_stdout():
            temp_string = session["resp"].read_stdout()
            print("STDOUT: %s" % temp_string)
            emit(
                'server_response',
                {'data': temp_string}
            )
        if session["resp"].peek_stderr():
            temp_string = session["resp"].read_stderr()
            print("STDERR: %s" % temp_string)
            emit(
                'server_response',
                {'data': temp_string}
            )
    disconnect()

@socketio.on('submit_event', namespace='/test')
def test_message(message):
    print("submit_event.")
    if message.get("data"):
        session["resp"].write_stdin(message.get("data") + "\n")

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)
    if session.get("resp"):
        session["resp"].close()


if __name__ == '__main__':
    socketio.run(app, debug=True)

