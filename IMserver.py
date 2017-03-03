#JulieSalah's IM Project

import argparse, select, socket, sys

parser = argparse.ArgumentParser(description='Host or Sender')
parser.add_argument('--s', help = 'designate machine as server', action = "store_true")
parser.add_argument('--c', help = 'designate machine as client, please give client name as an argument')
args = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 9998

server_address = ('localhost', port)

sock.bind(server_address)
print "socket binded to %s" %(port)

sock.listen(5)
print "socket is listening"

input = [sock,sys.stdin]

programRunning = True

while True:
    inputready, outputready = select.select(input, [], []) #type of input

    for s in inputready:

        sock.connect('localhost', port)

        print sock.recv(1024)

        if s == sock:
            # handle the server socket
            client, address = sock.accept()
            input.append(client)
            print 'Got connection from', address
            # send a thank you message to the client.
            client.send('Thank you for connecting')
            # Close the connection with the client
            client.close()

        else:
            # handle client input
            junk = sys.stdin.readline()
            programRunning = False