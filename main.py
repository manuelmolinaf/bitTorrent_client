
import os
import uuid
from collections import OrderedDict
import requests
import socket
import json
import queue
import threading
import bencodepy
import hashlib
from urllib.parse import quote, urlencode
import time


def tcp_listener():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = ('localhost', 6881)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(2)

    while True:
        # Wait for a connections
        print('waiting for a connection')

        connection, client_address = sock.accept()
        print('connection from', client_address)


# threading.Thread(target=tcp_listener).start()

# Get meta info dictionary
meta_info = OrderedDict(bencodepy.decode_from_file('test3.torrent'))

info_hash = hashlib.sha1(bencodepy.encode(meta_info[b'info']))


peer_id = '-MN0001-' + str(time.time())[-12:]

params = {
    'info_hash': info_hash.digest(),
    'peer_id': peer_id,
    'port': 6881,
    'uploaded': 0,
    'downloaded': 0,
    'left': 1461097787,
    'compact': 0,
    'event': 'started',

}

r = requests.get(url=meta_info[b'announce'].decode('utf-8') + '?' + urlencode(params))
print(r)
print(r.content)
