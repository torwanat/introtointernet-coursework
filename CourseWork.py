#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# The modules required
import sys
import socket
import struct
import random
from textwrap import wrap

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

client_keys = []
server_keys = []
 
def send_and_receive_tcp(address, port, message):
    print("You gave arguments: {} {} {}".format(address, port, message))
    global client_keys, server_keys

    message += "\r\n"
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
    try:
        message_parts = decoded_message.split('\r\n')
        server_keys = message_parts[1:-1]
        print(server_keys)

        hello, cid, udp_port = message_parts[0].split(' ')
        # Continue to UDP messaging. You might want to give the function some other parameters like the above mentioned cid and port.
        send_and_receive_udp(address, int(udp_port), cid)
    except Exception as e:
        print(e)

    return
 
 
def send_and_receive_udp(address, port, cid):
    '''
    Implement UDP part here.
    '''
    print("This is the UDP part. Implement it yourself.")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    current_client_key = 0
    current_server_key = 0

    message_body = "Hello from " + cid + "\r\n"
    # encrypted_message_body = encryption(message_body, True, current_client_key)
    # current_client_key += 1
    # data = struct.pack(DATAGRAM_FORMAT, cid.encode(), True, True, 0, len(encrypted_message_body), encrypted_message_body.encode())

    data = struct.pack(DATAGRAM_FORMAT, cid.encode(), True, True, 0, len(message_body), message_body.encode())
    s.sendto(data, (address, port))

    message_body_parts = []
    while True:
        received_data = s.recv(1024)
        cid, ack, eom, data_remaining, content_length, content = struct.unpack(DATAGRAM_FORMAT, received_data)

        message_body_parts.append(content.decode()[:content_length])

        if eom:
            print("EOM " + message_body_parts[0])
            break

        if data_remaining == 0:
            reply_parts = process_message(message_body_parts, cid, current_server_key, current_client_key)
            current_client_key += 1
            current_server_key += 1

            for reply in reply_parts:
                s.sendto(reply, (address, port))

            message_body_parts = []


    s.close()

    return

def process_message(message_body_parts, cid, current_server_key, current_client_key):
    decrypted_message_body = ''
    parity = True

    for message_part in message_body_parts:
        message_part_without_parity = check_message_parity(message_part)

        if message_part_without_parity == "WRONG_PARITY":
            print("Parity fail")
            parity = False
            break
        else:
            # decrypted_message_part = encryption(message_part, False, current_server_key)
            # print(decrypted_message_part)
            # decrypted_message_body += decrypted_message_part
            decrypted_message_body += message_part_without_parity

    print("Message: ", decrypted_message_body)
    if parity:
        reply_body = ' '.join(decrypted_message_body.replace('\r\n', '').split(' ')[::-1])
    else:
        reply_body = "Send again"

    print("Reply: ", reply_body)

    reply_pieces_length = []
    reply_message_parts = []

    for piece in pieces(reply_body):
        reply_pieces_length.append(len(piece))
        # encrypted_reply_part = encryption(piece, True, current_client_key)
        # parity_reply_part = add_parity_to_message(encrypted_reply_part)
        parity_reply_part = add_parity_to_message(piece)
        reply_message_parts.append(parity_reply_part)

    remaining = sum(reply_pieces_length)

    reply_parts = []
    for i, part in enumerate(reply_message_parts):
        remaining -= reply_pieces_length[i]
        reply_parts.append(struct.pack(DATAGRAM_FORMAT, cid, parity, True, remaining, reply_pieces_length[i], part.encode()))

    return reply_parts

def pieces(message, length = 64):
    chunks = [message[i:i + length] for i in range(0, len(message), length)]
    return chunks

def encryption(message, encrypt, current_key):
    print("Encrypting: ", encrypt, " message ", message, " with key ", current_key)
    print(server_keys)

    if encrypt:
        if current_key >= len(client_keys):
            return message
        key = client_keys[current_key]
    else:
        if current_key >= len(server_keys):
            return message
        key = server_keys[current_key]

    result = ''

    print(current_key, key, client_keys, len(key))
    for i, char in enumerate(message):
        result += chr((ord(char) ^ ord(key[i])))

    return result

# def encrypt_message(message):
#     global current_client_key
#
#     if current_client_key >= len(client_keys):
#         return message
#
#     key = client_keys[current_client_key]
#     current_client_key += 1
#
#     encrypted_message = ''
#     for i, char in enumerate(message):
#         encrypted_message += chr((ord(char) ^ ord(key[i])))
#
#     return encrypted_message
#
# def decrypt_message(message):
#     global current_server_key
#
#     if current_server_key >= len(server_keys):
#         return message
#
#     key = server_keys[current_server_key]
#     current_server_key += 1
#
#     decrypted_message = ''
#     for i, char in enumerate(message):
#         decrypted_message += chr((ord(char) ^ ord(key[i])))
#
#     return decrypted_message

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
