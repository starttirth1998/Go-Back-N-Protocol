import socket
import hashlib
import os
import time
import mimetypes
import random
import signal
import sys

client_host = socket.gethostname()
#client_host = socket.gethostbyname('10.1.38.45')
client_port = 9999
server_host = socket.gethostname()
#server_host = socket.gethostbyname('10.42.0.65')
#server_host = gethostbyname"localhost"
server_port = 9998

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientsocket.bind((client_host,client_port))

print "Press ENTER after starting server",
temp = raw_input()

base = 1
print "Window Size:",
window_size = input()
window = []
mss = 512
header_len = 8
print "Timeout:",
TIMEOUT = input()

class AlarmException(Exception):
    pass

def alarmHandler(signum, frame):
    raise AlarmException

def checksum(m):
    l = len(m)
    if l%2 != 0:
        m += '9'
        l+=1
    csum=0
    for i in range(0,l,2):
        csum = ((csum + (ord(m[i]) + (ord(m[i+1]) << 8))) & 0xffff) + ((csum + (ord(m[i]) + (ord(m[i+1]) << 8))) >> 16)
    return str(~csum & 0xffff)

def recv_ack(expected_seq_num):
    signal.signal(signal.SIGALRM, alarmHandler)
    signal.alarm(TIMEOUT)
    try:
        data, taddr = clientsocket.recvfrom(1024)
    except AlarmException:
        return 0
    '''
    print taddr[0],server_host
    if taddr[0] != server_host:
        print "Packet from unexpected server"
        return 0
    '''
    print data, expected_seq_num
    if str(expected_seq_num)!=str(data):
        print "Wrong Acknowledgement"
        return 0
    else:
        print "Right Acknowledgement"
        return 1

def create_pkt(file_data):
    seq_num = 0
    pkts = []
    sent = 0
    to_send = min(mss - header_len, len(file_data) - sent)

    while to_send > 0:
        info = ""
        data = file_data[sent:sent+to_send]
        info += str(seq_num) + ';;eNdOfFiLe;;' + checksum(file_data[sent:sent+to_send]) + ';;eNdOfFiLe;;' + str(data)
        #print seq_num,info
        pkts.append(info)
        sent += to_send
        to_send = min(mss - header_len, len(file_data) - sent)
        seq_num += 1
    return pkts

def rdt_send(file_data):
    pkts = create_pkt(file_data)

    last_unacked = 0
    unacked = 0

    print "Send Length", len(pkts)
    clientsocket.sendto(str(len(pkts)),(server_host,server_port))
    temp, addr = clientsocket.recvfrom(1)
    start_time = time.time()
    while last_unacked < len(pkts):
        #print unacked, window_size
        if unacked < window_size and (unacked + last_unacked) < len(pkts):
            #print unacked + last_unacked,"\n",pkts[unacked + last_unacked]
            clientsocket.sendto(pkts[unacked + last_unacked],(server_host,server_port))
            unacked += 1
            continue
        else:
            pkt_recv = recv_ack(last_unacked)
            if pkt_recv == 1:
                unacked = unacked - 1
                last_unacked = last_unacked + 1
                start_time = time.time()
                continue
            '''
            else if pkt_recv == 0:
                unacked = 0
                start_time = time.time()
                continue
            '''
            #pkt_recv, addr = clientsocket.recvfrom(1024)
            print (time.time() - start_time), TIMEOUT
            if (time.time() - start_time >= TIMEOUT):
                print "TIMEOUT"
                unacked = 0
                start_time = time.time()
                continue
    print "File Succesfully transfered"

print "Filename:",
filename = raw_input()
try:
    f = open(filename,'rb')
    data = f.read()
    f.close()

except:
    print "File not Found"
    sys.exit(E_FILE_READ_FAIL)

if data == "":
    print "No data read from file"
    sys.exit(E_FILE_READ_FAIL)

rdt_send(data)
clientsocket.close()

'''
while window:
    if (next_seq_num < base + window_size):
        client.sendto(next_seq_num,(host,port))
        client.recvfrom(1)
        client.sendto(data)
        client.recvfrom(1)
        hash_val = md5(data)
        client.sendto(hash_val)
        client.recvfrom(1)
'''
