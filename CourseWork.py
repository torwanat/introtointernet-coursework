#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# The modules required
import sys
import socket
import struct
import random

'''
This is a template that can be used in order to get started. 
It takes 3 commandline arguments and calls function send_and_receive_tcp.
in haapa7 you can execute this file with the command: 
python3 CourseWork.py <ip> <port> <message> 

Functions send_and_receive_tcp contains some comments.
If you implement what the comments ask for you should be able to create 
a functioning TCP part of the course work with little hassle.  

'''

DATAGRAM_FORMAT = '!8s??HH128s'

current_client_key = 0
current_server_key = 0
client_keys = []
server_keys = []
 
def send_and_receive_tcp(address, port, message):
    print("You gave arguments: {} {} {}".format(address, port, message))
    global client_keys, server_keys

    message += "\n"
    for _ in range(20):
        key = generate_key()
        client_keys.append(key)
        message += key + "\r\n"

    message += ".\r\n"

    print(message)
    # create TCP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect socket to given address and port
    s.connect((address, port))
    # python3 sendall() requires bytes like object. encode the message with str.encode() command
    encoded_message = message.encode('utf-8')
    # send given message to socket
    s.send(encoded_message)
    # receive data from socket
    received_message = s.recv(1024)
    # data you received is in bytes format. turn it to string with .decode() command
    decoded_message = received_message.decode('utf-8')
    # print received data
    print(decoded_message)
    # close the socket
    s.close()
    # Get your CID and UDP port from the message
    message_parts = decoded_message.split('\r\n')
    server_keys = message_parts[1:-1]

    hello, cid, udp_port = message_parts[0].split(' ')
    # Continue to UDP messaging. You might want to give the function some other parameters like the above mentioned cid and port.
    send_and_receive_udp(address, int(udp_port), cid)
    return
 
 
def send_and_receive_udp(address, port, cid):
    '''
    Implement UDP part here.
    '''
    print("This is the UDP part. Implement it yourself.")
    global current_server_key

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message_body = "Hello from " + cid + "\r\n"
    encrypted_message_body = encrypt_message(message_body)
    data = struct.pack(DATAGRAM_FORMAT, cid.encode(), True, True, 0, len(encrypted_message_body), encrypted_message_body.encode())
    s.sendto(data, (address, port))

    while True:
        received_data = s.recv(1024)
        cid, ack, eom, data_remaining, content_length, content = struct.unpack(DATAGRAM_FORMAT, received_data)

        message_body = content.decode()[:content_length]

        if eom:
            print("EOM " + message_body)
            break

        message_without_parity = check_message_parity(message_body)

        if message_without_parity == "WRONG_PARITY":
            reply_body = "Send again"
            print("Parity fail")
            current_server_key += 1
            ack_bit = False
        else:
            decrypted_message_body = decrypt_message(message_without_parity)
            print(decrypted_message_body)
            reply_body = ' '.join(decrypted_message_body.replace('\r\n', '').split(' ')[::-1])
            ack_bit = True

        print(reply_body)

        reply_body_length = len(reply_body)
        encrypted_reply_body = encrypt_message(reply_body)
        parity_reply_body = add_parity_to_message(encrypted_reply_body)

        reply = struct.pack(DATAGRAM_FORMAT, cid, ack_bit, True, 0, reply_body_length, parity_reply_body.encode())
        s.sendto(reply, (address, port))

    s.close()

    return

def encrypt_message(message):
    global current_client_key

    if current_client_key >= len(client_keys):
        return message

    key = client_keys[current_client_key]
    current_client_key += 1

    encrypted_message = ''
    for i, char in enumerate(message):
        encrypted_message += chr((ord(char) ^ ord(key[i])))

    return encrypted_message

def decrypt_message(message):
    global current_server_key

    if current_server_key >= len(server_keys):
        return message

    key = server_keys[current_server_key]
    current_server_key += 1

    decrypted_message = ''
    for i, char in enumerate(message):
        decrypted_message += chr((ord(char) ^ ord(key[i])))

    return decrypted_message

def generate_key():
    return ''.join(random.choices("0123456789ABCDEF", k=64))

def check_message_parity(parity_message):
    message = ''
    for char in parity_message:
        # print(char)
        char_value = ord(char)
        parity_bit = (char_value & 1)
        char_value >>= 1
        # print("Parity " + str(parity_bit) + " char " + chr(char_value))
        if parity_bit == get_parity(char_value):
            message += chr(char_value)
        else:
            message = "WRONG_PARITY"
            break

    return message

def add_parity_to_message(message):
    parity_message = ''
    for char in message:
        char_value = ord(char)
        char_value <<= 1
        char_value += get_parity(char_value)
        parity_message += chr(char_value)
    return parity_message

def get_parity(n):
     while n > 1:
            n = (n >> 1) ^ (n & 1)
     return n
 
def main():
    USAGE = 'usage: %s <server address> <server port> <message>' % sys.argv[0]
 
    try:
        # Get the server address, port and message from command line arguments
        server_address = str(sys.argv[1])
        server_tcpport = int(sys.argv[2])
        message = str(sys.argv[3])
    except IndexError:
        print("Index Error")
    except ValueError:
        print("Value Error")
    # Print usage instructions and exit if we didn't get proper arguments
        sys.exit(USAGE)
 
    send_and_receive_tcp(server_address, server_tcpport, message)
 
 
if __name__ == '__main__':
    # Call the main function when this script is executed
    main()
