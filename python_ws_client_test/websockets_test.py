import asyncio
import websockets
import ssl

ADMIN_TOKEN = "Bearer token-dt5mj:f87g97szf7chsdtcxrlr4scd8wjm6jzqwz6r7gpxmbh66v8v2mc88p"
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def hello():
    uri = "wss://192.168.56.101/k8s/clusters/c-fcwn9/api/v1/namespaces/john-namespace/pods/k8s-ws-7748b986cf-rq4r5/exec?container=k8s-ws&stdout=1&stdin=1&stderr=1&tty=1&command=%2Fbin%2Fsh&command=-c&command=TERM%3Dxterm-256color%3B%20export%20TERM%3B%20%5B%20-x%20%2Fbin%2Fbash%20%5D%20%26%26%20(%5B%20-x%20%2Fusr%2Fbin%2Fscript%20%5D%20%26%26%20%2Fusr%2Fbin%2Fscript%20-q%20-c%20%22%2Fbin%2Fbash%22%20%2Fdev%2Fnull%20%7C%7C%20exec%20%2Fbin%2Fbash)%20%7C%7C%20exec%20%2Fbin%2Fsh"

    header = {
        "Authorization": ADMIN_TOKEN
    }
    async with websockets.connect(
        uri, ssl=ssl_context,
        extra_headers = header,
        # this is the subprotocol for rancher /logs
        #subprotocols = ['base64.binary.k8s.io']
        subprotocols = ['base64.channel.k8s.io']
    ) as websocket:

        # "ls\n" as shown by rancher websocket on browser.
        await websocket.send("0bA==")
        await websocket.send("0cw==")
        await websocket.send("0DQ==")
        while websocket:
            greeting = await websocket.recv()
            print(type(greeting))
            print(f"{greeting}")

asyncio.get_event_loop().run_until_complete(hello())

