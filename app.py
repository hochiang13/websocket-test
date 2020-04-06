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
import time

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
    # need a first event after connect event to start stream to kubernetes thread.
    # Tried starting a background thread in the connect event function,
    #   it doesn't work because it is outside of the application context,
    #   and socketio.emit will send event to all clients.

    print("first_event.")
    token = request.headers.get("Authorization")
    cluster_id = request.headers.get("clusterid")
    namespace = request.args.get("namespace")
    pod = request.args.get("pod")

    load_kubernetes_config(
        token=token,
        cluster_id=cluster_id
    )
    api = core_v1_api.CoreV1Api()
    exec_command = ['/bin/sh']
    try:
        session["resp"] = stream(
            api.connect_get_namespaced_pod_exec,
            name=pod,
            namespace=namespace,
            command=exec_command,
            stderr=True, stdin=True,
            stdout=True, tty=False,
            _preload_content=False
        )
    except Exception as e:
        print(f"Cannot stream: {str(e)}")
        disconnect()
        return
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

@socketio.on('submit_event', namespace='/shell')
def shell_submit(message):
    print("submit_event.")
    if message.get("data"):
        session["resp"].write_stdin(message.get("data") + "\n")

@socketio.on('disconnect', namespace='/shell')
def shell_disconnect():
    print('Client disconnected', request.sid)
    if session.get("resp"):
        session["resp"].close()


if __name__ == '__main__':
    socketio.run(app, debug=False)

