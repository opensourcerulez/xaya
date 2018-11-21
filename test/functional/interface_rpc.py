#!/usr/bin/env python3
# Copyright (c) 2018 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Tests some generic aspects of the RPC interface."""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, str_to_b64str

import http.client
import json
import urllib.parse

class RPCInterfaceTest(BitcoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True

    def send_request(self, request):
        self.conn.request('POST', '/', json.dumps(request), self.headers)
        out = self.conn.getresponse().read()
        return json.loads(out.decode('ascii'))

    def test_batch_request(self):
        self.log.info("Testing basic JSON-RPC batch request...")

        request = [
            # Two basic requests that will work fine.
            {"method": "getblockcount", "id": 1},
            {"method": "getbestblockhash", "id": 2},
            # Request that will fail.  The whole batch request should still
            # work fine.
            {"method": "invalidmethod", "id": 3},
        ]
        results = self.send_request(request)

        result_by_id = {}
        for res in results:
            result_by_id[res["id"]] = res

        assert_equal(result_by_id[1]['error'], None)
        assert_equal(result_by_id[1]['result'], 10)

        assert_equal(result_by_id[2]['error'], None)
        assert_equal(result_by_id[2]['result'], self.node.getbestblockhash())

        assert_equal(result_by_id[3]['error']['code'], -32601)
        assert_equal(result_by_id[3]['result'], None)

    def run_test(self):
        self.node = self.nodes[0]
        self.node.generate(10)

        url = urllib.parse.urlparse(self.node.url)
        authpair = url.username + ':' + url.password
        self.headers = {"Authorization": "Basic " + str_to_b64str(authpair)}

        self.conn = http.client.HTTPConnection(url.hostname, url.port)
        self.conn.connect()

        self.test_batch_request()


if __name__ == '__main__':
    RPCInterfaceTest().main()
