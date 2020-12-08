import struct
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

    return len_id + protocol_id + reserved + str(p_info_hash) + str(p_peer_id)


def peer_connection(p_handshake, host, port):

    data = bytes(68)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.send(p_handshake)
        data = s.recv(68)

    except:
        print('could not connect to ' + host)
        return

    handshake_res = tuple(struct.unpack('>B19s8x20s20s', data))

    if handshake_res[3]:
        bitfield_length = struct.unpack('>I', bytes(s.recv(4)))[0]
        bitfield = s.recv(bitfield_length)

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


handshake = generate_handshake(info_hash, peer_id).encode('utf-8')

for peer in tracker_response[b'peers']:
    threading.Thread(target=peer_connection, args=(handshake, peer[b'ip'].decode('utf-8'), peer[b'port'])).start()
