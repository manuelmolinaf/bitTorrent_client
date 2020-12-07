import asyncio
from collections import OrderedDict
from struct import pack
import requests
import socket
import threading
import bencodepy
import hashlib
from urllib.parse import urlencode
import time

meta_info = OrderedDict(bencodepy.decode_from_file('test2.torrent'))

info_hash = hashlib.sha1(bencodepy.encode(meta_info[b'info'])).digest()

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
        'info_hash': info_hash,
        'peer_id': peer_id,
        'port': 6881,
        'uploaded': 0,
        'downloaded': 0,
        'left': get_torrent_size(),
        'compact': 0,
        'event': 'started',
    }
    return params


def generate_handshake(p_info_hash, p_peer_id):
    protocol_id = "BitTorrent protocol"
    len_id = str(len(protocol_id))
    reserved = "00000000"

    return len_id + protocol_id + reserved + p_info_hash + p_peer_id


def send_receive_handshake(handshake, host, port):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(handshake)

    data = s.recv(len(handshake))
    s.close()

    return data


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
print(tracker_response[b'peers'])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

loop = asyncio.get_event_loop()

# for peer in tracker_response[b'peers']:
#     handshake = generate_handshake()
