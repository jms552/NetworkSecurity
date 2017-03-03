#portscanner project
#julie Salah

import socket, sys
import random
import time


host = sys.argv[1]
countports = 0
r = list(range(1, 65536))
random.shuffle(r)

start = time.time()
print ("Program start time: {}".format(start))

for port in r:

    try:
    
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock.settimeout(3)
        scanner = sock.connect_ex((host, port))

        if scanner == 0:
            print ("Port {}: Open".format(port))
            info = socket.getservbyport(port)
            print ("Port Information: {}".format(info))
            countports += 1
            sock.close()
        
        else:
            print ("Port {}: Closed".format(port))
            
    
    

    except socket.error:
        print ("No connection")
        


stop = time.time()
timetaken = stop - start
print ("Program stop time: {}".format(stop))
print ("Number of open ports: {}".format(countports))
print ("Scanned ports per second: {}".format(65536/timetaken))
print ("Program Run time: {}".format(timetaken))