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


meta_info = OrderedDict(bencodepy.decode_from_file('test3.torrent'))

info_hash = hashlib.sha1(bencodepy.encode(meta_info[b'info']))

peer_id = '-MN0001-' + str(time.time())[-12:]


def get_torrent_size():

    file_size = 0

    if b'files' in meta_info[b'info']:
        for file in meta_info[b'info'][b'files']:
            file_size += int(file[b'length'])
    else:
        file_size = meta_info[b'info'][b'length']

    return file_size


def get_params():
    params = {
        'info_hash': info_hash.digest(),
        'peer_id': peer_id,
        'port': 6881,
        'uploaded': 0,
        'downloaded': 0,
        'left': get_torrent_size(),
        'compact': 0,
        'event': 'started',
    }
    return params


def tcp_listener():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = ('localhost', 6881)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen()

    while True:
        # Wait for connections
        print('waiting for a connection')

        connection, client_address = sock.accept()
        print('connection from', client_address)


# threading.Thread(target=tcp_listener).start()

tracker_response = OrderedDict()

while True:
    try:
        response = requests.get(url=meta_info[b'announce'].decode('utf-8') + '?' + urlencode(get_params()))
        print(response)
        tracker_response = OrderedDict(bencodepy.decode(response.content))
        break

    except requests.exceptions.RequestException as e:
        print('Tracker timed out. Trying again in 3 seconds.')
        time.sleep(3)


print(tracker_response.keys())
print(tracker_response)
print(tracker_response[b'interval'])
print(len(tracker_response[b'peers']))

