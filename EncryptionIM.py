#JulieSalah's encrypedIM Project
#python 3.5.1

import argparse, select, socket, sys
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256

#https://docs.python.org/3/library/argparse.html
parser = argparse.ArgumentParser(description='client or server')
parser.add_argument('--s', help = 'server', action = "store_true")
parser.add_argument('--c', help = 'client')
parser.add_argument('-authkey', help = "AHHHH Auth key!! - k2")
parser.add_argument('-confkey', help = "AHHHH conf key - k1")
args = parser.parse_args()


port = 9999

if args.confkey is None or args.authkey is None:
    print("Need keys")
    sys.exit()


key1 = args.confkey
key2 = args.authkey
SHAstuff = SHA256.new()
SHAstuff.update(key1.encode('utf-8'))
key1 = SHAstuff.digest()
SHAstuff.update(key2.encode('utf-8'))
key2 = SHAstuff.digest()

#Cipher Block Chaining
mode = AES.MODE_CBC


if args.s and args.c is None: #server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', port))
    sock.listen(5)
    client, address = sock.accept()
    input = [sock, client, sys.stdin]


if args.c is not None and not args.s: #client
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((args.c, port))
    input = [sock, sys.stdin]

#keep the program running while you are sending/receiving messages
programRunning = True
while programRunning:

    (inputready, _, _) = select.select(input, [], []) #checks if there is input from potential readers/writers

    for stuff in inputready:

        if stuff is sys.stdin: #input
            iv = Random.get_random_bytes(16)
            # creates the cipher obj
            aesObj = AES.new(key1, mode, iv)
            data = sys.stdin.readline() #reads unsent message
            if not data:
                programRunning = False
                sock.close()
            if (len(data) % 16 != 0): #padding if the text isnt the block size - avoids ambiguity
                padding = 16 - len(data) % 16
                data += padding * ' '
            data = aesObj.encrypt(data) #encrypting the data
            authObj = HMAC.new(key2, data, SHA256) #hashing
            hashed = authObj.digest()
            #print ('actual:', hashed)
            #send input
            if args.s:
                client.send(iv + hashed + data)
            else:
                sock.send(iv + hashed + data)

        else:
            #receive AES key, IV, and hmac
            iv = stuff.recv(16, socket.MSG_WAITALL)
            sent = stuff.recv(32, socket.MSG_WAITALL)
            data = stuff.recv(1024)
            if not data:
                programRunning = False
                sock.close()
            authObj = HMAC.new(key2, data, SHA256)
            hashed = authObj.digest()
            if sent != hashed:
                print("Corruption!!") #check authenticity
                programRunning = False
            #else:
                #print ('authentic:', hashed)
            aesObj = AES.new(key1, mode, iv)
            data = aesObj.decrypt(data) #decryption
            print(data)

sock.close()
