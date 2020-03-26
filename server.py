import socket
import select
from _datetime import datetime
import time
import csv

# initial variables
HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()
sockets_list = [server_socket]
clients = {}


# handles message receiving
def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header): # user disconnected
            return False
        message_length = int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}
    except:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets: # got a new connection
        if notified_socket == server_socket:
            # getting unique client socket and address
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)
            if user is False :
                continue

            sockets_list.append(client_socket)
            # saving username to csv with flag and receiving info about connection
            clients[client_socket] = user
            date_time_stamp = datetime.fromtimestamp(time.time())
            log = open(f"log\server{date_time_stamp.strftime('%Y-%m-%d')}.log", 'a')
            print(
                f"[{date_time_stamp.strftime('%Y-%m-%d %H:%M:%S')}]: Accepted new connection from {client_address[0]}:{client_address[1]} username: {user['data'].decode('utf-8')}",
                file=log)
            log.close()

        else: # if notified socket is not a server socket - means message
            message = receive_message(notified_socket)

            if message is False: # if client disconnects message would be empty
                date_time_stamp = datetime.fromtimestamp(time.time())
                log = open(f"log\server{date_time_stamp.strftime('%Y-%m-%d')}.log", 'a')
                print(
                    f"[{date_time_stamp.strftime('%Y-%m-%d %H:%M:%S')}]: Closed connection for {clients[notified_socket]['data'].decode('utf-8')}",
                    file=log)
                log.close()
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            # message is received - print to server.log info about it
            user = clients[notified_socket]
            log = open(f"log\server{date_time_stamp.strftime('%Y-%m-%d')}.log", 'a')
            print(
                f"[{date_time_stamp.strftime('%Y-%m-%d %H:%M:%S')}]: Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}",
                file=log)
            log.close()

            # sending message to all clients
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
