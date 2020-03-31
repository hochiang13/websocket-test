import websocket, ssl
import base64

ADMIN_TOKEN = "token-hxfsx:kqdf44kck5n4pdnjs4v22hchlvdb95g59xt5nmj75ldsgx2wnq695f"


url = "wss://10.62.164.163/k8s/clusters/c-6rlzw/api/v1/namespaces/debugger/pods/curl-debugger-56dc9dcd9b-q8kgn/exec?container=curl-debugger&stdout=1&stdin=1&stderr=1&tty=1"
#url += "&command=%2Fbin%2Fsh&command=-c&command=TERM%3Dxterm-256color%3B%20export%20TERM%3B%20%5B%20-x%20%2Fbin%2Fbash%20%5D%20%26%26%20(%5B%20-x%20%2Fusr%2Fbin%2Fscript%20%5D%20%26%26%20%2Fusr%2Fbin%2Fscript%20-q%20-c%20%22%2Fbin%2Fbash%22%20%2Fdev%2Fnull%20%7C%7C%20exec%20%2Fbin%2Fbash)%20%7C%7C%20exec%20%2Fbin%2Fsh"

url += "&command=ls"

#url = "wss://10.62.164.163/k8s/clusters/c-6rlzw/api/v1/namespaces/efk/pods/efk-kibana-5dc5c455df-bk776/log?container=kibana&tailLines=500&follow=true&timestamps=true&previous=false"

wss = websocket.create_connection(
    url,
    sslopt={"cert_reqs": ssl.CERT_NONE},
    header={"Authorization": "bearer " + ADMIN_TOKEN}
)
print(wss)
while wss:
    print(wss.recv_frame())
wss.send("ls")
print(wss.recv_frame())
wss.close()

