import socket
import errno
import sys
from _datetime import datetime
import time
from threading import Thread

# initial variables
HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP,PORT))
client_socket.setblocking(False)

# declaring username
my_username = input("Your username: ")

# sending username to server
username = my_username.encode('utf-8')
username_header = f'{len(username):<{HEADER_LENGTH}}'.encode('utf-8')
client_socket.send(username_header+username)


# successful connection
while True:
    date_time_stamp = datetime.fromtimestamp(time.time())
    message = input(f"[{date_time_stamp.strftime('%Y-%m-%d %H:%M:%S')}]: {my_username} > ")

    # if message is written - print it for client and send to server
    if message:
        message = message.encode('utf-8')
        message_header = f'{len(message) :< {HEADER_LENGTH}}'.encode('utf-8')
        client_socket.send(message_header + message)
    try:
        # receive messages
        while True:
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print("Connection closed by the server")
                sys.exit()

            # decoding message
            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            # printing message with system time from client [should be from server - working on it]
            date_time_stamp = datetime.fromtimestamp(time.time())
            print(f"[{date_time_stamp.strftime('%Y-%m-%d %H:%M:%S')}]: {username} > {message}")


# handling exceptions
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error', str(e))
            sys.exit()
        continue

    except Exception as e:
        print('General error',str(e))
        sys.exit()



