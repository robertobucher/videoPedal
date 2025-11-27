#!/usr/bin/python3

import socket
import os

socket_path = '/tmp/my_socket'

def send_key(key):
  print(key)

############ START ###########

try:
    os.unlink(socket_path)
except OSError:
    if os.path.exists(socket_path):
        raise

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(socket_path)

print('Start server...')
server.listen(1)

connection, client_address = server.accept()

try:
    while True:
        data = connection.recv(1024)
        if not data:
            break
        key = int(data.decode())
        send_key(key)

finally:
    # close the connection
    connection.close()
    # remove the socket file
    os.unlink(socket_path)



