import socket
import hashlib
import os
import time
import mimetypes
import random
import signal
import sys

packet_loss_prob = 0.2

server_host = socket.gethostname()
#server_host = socket.gethostbyname('10.1.38.45')
server_port = 9998
#client_host = socket.gethostbyname('10.42.0.1')
client_host = socket.gethostname()
client_port = 9999

serversocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
serversocket.bind((server_host, server_port))

def checksum(m):
    l = len(m)
    if l%2 != 0:
        m += '9'
        l+=1
    csum=0
    for i in range(0,l,2):
        csum = ((csum + (ord(m[i]) + (ord(m[i+1]) << 8))) & 0xffff) + ((csum + (ord(m[i]) + (ord(m[i+1]) << 8))) >> 16)
    return str(~csum & 0xffff)

def send_ack(expected_seq_num):
    #print expected_seq_num
    serversocket.sendto(str(expected_seq_num), (client_host, client_port))
    expected_seq_num+=1
    return expected_seq_num
#serversocket.listen(5)

def rdt_recv():
    f = open("output","wb")
    expected_seq_num = 0

    len_data, addr = serversocket.recvfrom(1024)
    serversocket.sendto("b",(client_host,client_port))
    print len_data
    len_data = int(len_data)
    while len_data > 0:
        file_data, addr = serversocket.recvfrom(1024)
        info = file_data.split(';;eNdOfFiLe;;')
        recv_seq_num = info[0]
        recv_checksum = info[1]
        recv_data = info[2]
        #print recv_data

        #print recv_seq_num,":::",expected_seq_num
        #print str(checksum(recv_data)),"+++",str(recv_checksum)

        if str(expected_seq_num) == str(recv_seq_num):
            if str(checksum(recv_data)) == str(recv_checksum):
                r = random.random()
                if r <= packet_loss_prob:
                    print "Packet Loss: ", recv_seq_num
                    continue
                f.write(recv_data)
                expected_seq_num = send_ack(expected_seq_num)
                len_data = len_data - 1

    f.close()

rdt_recv()
serversocket.close()

'''
while True:
    try:
        print "Server Ready"
        data, addr = serversocket.recvfrom(1024)
'''
