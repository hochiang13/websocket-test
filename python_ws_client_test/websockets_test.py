import asyncio
import websockets
import ssl

ADMIN_TOKEN = "Bearer token-hxfsx:kqdf44kck5n4pdnjs4v22hchlvdb95g59xt5nmj75ldsgx2wnq695f"
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def hello():
    #uri = "wss://10.62.164.163/k8s/clusters/c-6rlzw/api/v1/namespaces/debugger/pods/curl-debugger-56dc9dcd9b-q8kgn/exec?container=curl-debugger&stdout=1&stdin=1&stderr=1&tty=1"
    #uri += "&command=%2Fbin%2Fsh&command=-c&command=TERM%3Dxterm-256color%3B%20export%20TERM%3B%20%5B%20-x%20%2Fbin%2Fbash%20%5D%20%26%26%20(%5B%20-x%20%2Fusr%2Fbin%2Fscript%20%5D%20%26%26%20%2Fusr%2Fbin%2Fscript%20-q%20-c%20%22%2Fbin%2Fbash%22%20%2Fdev%2Fnull%20%7C%7C%20exec%20%2Fbin%2Fbash)%20%7C%7C%20exec%20%2Fbin%2Fsh"

    #uri += "&command=ls"

    uri = "wss://10.62.164.163/k8s/clusters/c-6rlzw/api/v1/namespaces/efk/pods/efk-kibana-5dc5c455df-bk776/log?container=kibana&tailLines=500&follow=true&timestamps=true&previous=false"

    header = {
        "Authorization": ADMIN_TOKEN
    }
    async with websockets.connect(
        uri, ssl=ssl_context,
        extra_headers = header,
        subprotocols = ['base64.binary.k8s.io']
        #subprotocols = ['base64.channel.k8s.io']
    ) as websocket:
        #name = input("What's your name? ")

        #await websocket.send(name)
        #print(f"> {name}")
        while websocket:
            greeting = await websocket.recv()
            print(type(greeting))
            print(f"{greeting}")

asyncio.get_event_loop().run_until_complete(hello())

