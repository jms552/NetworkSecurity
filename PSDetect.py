from scapy.all import *
import datetime
import netifaces 
#import socket


ports = []
times = []

netifaces.ifaddresses('en0')
ip = netifaces.ifaddresses('en0')[2][0]['addr']
#print ip 

## main function
def customAction(packet):
    
    #ignore packets coming from self
    if(packet[0][1].src == ip):
    	return

    portnumber = packet[TCP].dport
   
    ports.append(portnumber)
    times.append(int(time.time()))
    currenttime = int(time.time())
    #print ports[0]
    #print times[0]
    #print currenttime

    consectutiveports = 0
    currentport = packet[TCP].dport

    for i in range (len(ports)-1, -1, -1):
    	#print i
    	if currenttime-5 > times[i]:
    		del times[i]
    		del ports[i]
    		#i = i-1
    	if len(ports)>30:
    		print ("Scanner detected. The scanner originated from host {}" .format(packet[0][1].src))

    #if you wanted to scan for consecutiveports
   	for i in range(len(ports)-1, 0, -1):
   		if ports[i] == currentport-1:
   			currentport = currentport-1
   			consectutiveports = consectutiveports+1
   		if consectutiveports >= 15:
   			print ("Scanner detected. The scanner originated from host {}" .format(packet[0][1].src))


#sniff filter
sniff(filter="tcp",prn=customAction)





