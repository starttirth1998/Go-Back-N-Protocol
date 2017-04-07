import socket
import hashlib
import os

host = socket.gethostname()
port = 9999

serversocket = socket.socket(AF_INET,SOCK_DGRAM)
serversocket.bind(host, port)
