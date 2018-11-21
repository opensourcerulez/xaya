#!/usr/bin/env python3

from test_framework.util import str_to_b64str

import http.client
import json
import urllib.parse

url = urllib.parse.urlparse("http://xaya:password@localhost:8396")
authpair = url.username + ':' + url.password
headers = {"Authorization": "Basic " + str_to_b64str(authpair)}

conn = http.client.HTTPConnection(url.hostname, url.port)
conn.connect()

def send_request(request, wantResult):
    conn.request('POST', '/', json.dumps(request), headers)
    resp = conn.getresponse()
    if not wantResult:
        print("Status code: %d" % resp.status)
    out = resp.read()
    if wantResult:
        return json.loads(out.decode('ascii'))
    return None

print("Preparing requests...")
requests = []
nextBlk = 0
for i in range(5):
    print("Request number %d..." % (i + 1))
    req = []
    for j in range(70000):
        blkhash = send_request({
            "method": "getblockhash",
            "params": [nextBlk],
        }, True)['result']
        req.append({
            "method": "getblock",
            "params": {
                "blockhash": blkhash,
                "verbosity": 2,
            },
            "id": nextBlk,
        })
        nextBlk += 1
    requests.append(req)

for req in requests:
    print("Sending request now...")
    send_request(req, False)
