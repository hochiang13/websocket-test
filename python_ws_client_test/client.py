import websocket, ssl
import base64

ADMIN_TOKEN = "Bearer token-dt5mj:f87g97szf7chsdtcxrlr4scd8wjm6jzqwz6r7gpxmbh66v8v2mc88p"

url = "wss://192.168.56.101/k8s/clusters/c-fcwn9/api/v1/namespaces/john-namespace/pods/k8s-ws-7748b986cf-rq4r5/exec?container=k8s-ws&stdout=1&stdin=1&stderr=1&tty=1&command=%2Fbin%2Fsh&command=-c&command=TERM%3Dxterm-256color%3B%20export%20TERM%3B%20%5B%20-x%20%2Fbin%2Fbash%20%5D%20%26%26%20(%5B%20-x%20%2Fusr%2Fbin%2Fscript%20%5D%20%26%26%20%2Fusr%2Fbin%2Fscript%20-q%20-c%20%22%2Fbin%2Fbash%22%20%2Fdev%2Fnull%20%7C%7C%20exec%20%2Fbin%2Fbash)%20%7C%7C%20exec%20%2Fbin%2Fsh"


wss = websocket.create_connection(
    url,
    sslopt={"cert_reqs": ssl.CERT_NONE},
    header={"Authorization": ADMIN_TOKEN},
    subprotocols=['base64.channel.k8s.io']
)
print(wss)

wss.send("0bA==")
wss.send("0cw==")
wss.send("0DQ==")

for i in range(0, 10):
    print(wss.recv())
wss.close()

