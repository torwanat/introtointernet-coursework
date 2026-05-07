#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# The modules required
import sys
import socket
import struct

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
 
def send_and_receive_tcp(address, port, message):
    print("You gave arguments: {} {} {}".format(address, port, message))
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
    hello, cid, udp_port = decoded_message.replace('\r\n', '').split(' ')
    # Continue to UDP messaging. You might want to give the function some other parameters like the above mentioned cid and port.
    send_and_receive_udp(address, int(udp_port), cid)
    return
 
 
def send_and_receive_udp(address, port, cid):
    '''
    Implement UDP part here.
    '''
    print("This is the UDP part. Implement it yourself.")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message_body = "Hello from " + cid + "\r\n"
    data = struct.pack(DATAGRAM_FORMAT, cid.encode(), True, True, 0, len(message_body), message_body.encode())
    s.sendto(data, (address, port))

    while True:
        received_data = s.recv(1024)
        cid, ack, eom, data_remaining, content_length, content = struct.unpack(DATAGRAM_FORMAT, received_data)

        message_body = content.decode()[:content_length]
        print(message_body)

        if eom:
            print("EOM")
            break

        reply_body = ' '.join(message_body.replace('\r\n', '').split(' ')[::-1])
        print(reply_body)

        reply = struct.pack(DATAGRAM_FORMAT, cid, True, True, 0, len(reply_body), reply_body.encode())
        s.sendto(reply, (address, port))

    s.close()

    return
 
 
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
