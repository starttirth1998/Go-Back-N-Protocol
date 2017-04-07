import socket
import hashlib
import os

def md5(filename):
    hasher = hashlib.md5()
    with open(filename,"rb") as f:
        buf = f.read(1024)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(1024)
    return hasher.hexdigest()

host = socket.gethostname()
port = 9999

client = socket.socket(AF_INET, SOCK_DGRAM)

base = 1
next_seq_num = 1
window_size = 5
window = []

filename = "s.py"
f = open(filename,'rb')
data = f.read(1024)
last_ack_received = time.time()

while window:
    if (next_seq_num < base + window_size):
        client.send(next_seq_num)
        client.recv(1)
        client.send(data)
        client.recv(1)
        hash_val = md5(data)
        client.send(hash_val)
        client.recv(1)
