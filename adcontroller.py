##
## A very low level AR.Drone2.0 Python controller
## by Micah Sherr
## (use at your own risk)
##




import socket
import sys, tty, termios

def getChar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def setBits( lst ):
    """
    set the bits in lst to 1.
    also set bits 18, 20, 22, 24, and 28 to one (since they should always be set)
    all other bits will be 0
    """
    res = 0
    for b in lst + [18,20,22,24,28]:
        res |= (1 << b)
    return res


def sendCommand( cmd ):
    global address
    global seqno
    global s
    #rint "DEBUG: Sending:  '%s'" % cmd.strip()
    s.sendto(cmd,address)
    seqno += 1


def reset():
    global seqno
    seqno = 1
    for i in xrange(1,25):
        sendCommand("AT*FTRIM=%d\r" % seqno )

        
def takeoff():
    global seqno
    sendCommand("AT*FTRIM=%d\r" % seqno )
    takeoff_cmd = setBits([9])
    print( takeoff_cmd ) 
    for i in xrange(1,25):
        sendCommand("AT*REF=%d,%d\r" % (seqno,takeoff_cmd))

        
def land():
    global seqno
    land_cmd = setBits([])
    for i in xrange(1,25):
        sendCommand("AT*REF=%d,%d\r" % (seqno,land_cmd))

def changeWifiName():
    global seqno
    sendCommand("""AT*CONFIG=%d,"network:ssid_single_player","DIRECT-DB-HP-Officejet 5740"\r""" % (seqno))
    print("""AT*CONFIG=%d,"network:ssid_single_player","Direct-DB-HP-Officejet 5740"\r""" % (seqno))
 
#movement with full power
negNumber = -1082130432
posNumber = 1065353216
negativeIndex = 0
positiveIndex = 4
posValueIndex = [0, 1048576000, 1056964608, 1061158912, 1065353216]
negValueIndex = [-1082130432, -1086324736, -1090519040, -1098907648, 0]

'''
def increaseSpeed():
    global positiveIndex
    global negativeIndex
    if( positiveIndex != 4 ): positiveIndex += 1
    if( negativeIndex != 0 ): negativeIndex -= 1
	
def decreaseSpeed():
    global positiveIndex
    global negativeIndex
    if( positiveIndex != 0 ): positiveIndex -= 1
    if( negativeIndex != 4 ): negativeIndex += 1
'''

def forward():
   global seqno
   global mode
   negNumber = negValueIndex[ negativeIndex ]
   for i in xrange(1,25):
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno, mode, 0, negNumber,0, 0))
        #LeftRight,ForwardBackward,UpDown,Turn

def backward():
   global seqno
   global mode
   posNumber = posValueIndex[ positiveIndex ]
   for i in xrange(1,25):
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno, mode, 0, posNumber,0, 0))
        #LeftRight,ForwardBackward,UpDown,Turn

def left():
   global seqno
   global mode
   negNumber = negValueIndex[ negativeIndex ]
   for i in xrange(1,25):
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno, mode, negNumber, 0,0, 0))
        #LeftRight,ForwardBackward,UpDown,Turn


def right():
   global seqno
   global mode
   posNumber = posValueIndex[ positiveIndex ]
   for i in xrange(1,25):
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno, mode, posNumber, 0,0, 0))
        #LeftRight,ForwardBackward,UpDown,Turn

def rightturn():
    global seqno
    global mode
    posNumber = posValueIndex[ positiveIndex ]
    for i in xrange(1,25):
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno, mode, 0, 0, 0, posNumber))
        #LeftRight,ForwardBackward,UpDown,Turn

def leftturn():
    global seqno
    global mode
    negNumber = negValueIndex[ negativeIndex ]
    for i in xrange(1,25):
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno, mode, 0, 0, 0, negNumber))
        #LeftRight,ForwardBackward,UpDown,Turn

def up():
    global seqno
    global mode
    posNumber = posValueIndex[ positiveIndex ]
    for i in xrange(1,25):
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno, mode, 0, 0, posNumber, 0))
        #LeftRight,ForwardBackward,UpDown,Turn

def down():
    global seqno
    global mode
    negNumber = negValueIndex[ negativeIndex ]
    for i in xrange(1,25):
        sendCommand("AT*PCMD=%d,%d,%d,%d,%d,%d\r" % (seqno, mode, 0, 0, negNumber, 0))
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
    print ("\tt       - takeoff")
    print ("\tl       - land")
    print ("\tw       - forward")
    print ("\ts       - backward")
    print ("\td       - right")
    print ("\ta       - left")
    print ("\tu       - up")
    print ("\tj       - down")
    print ("\th       - turn right")
    print ("\tk       - turn left")
    print ("\t+       - increase speed")
    print ("\t-       - decrease speed")
    print ("\tp       - changeWIFI")
    print ("\t(space) - emergency shutoff")



"""
NOTE:  This program assumes you are already connected to the
       drone's WiFi network.
"""
    
address = ('192.168.1.1',5556)
seqno = 1
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", 5554))
mode = 1

while True:
    printUsage()
    ch = getChar()
    
    if ch == 'q':
        exit(0)
    elif ch == 't':
        takeoff()
    elif ch == 'l':
        land()
    elif ch == 'w':
		forward()
    elif ch == 's':
        backward()
    elif ch == 'd':
        right()
    elif ch == 'a':
        left()
    elif ch == 'u':
        up()
    elif ch == 'j':
        down()
    elif ch == 'h':
    	leftturn()
    elif ch == 'k':
    	rightturn()
    elif ch == 'p':
        changeWifiName()
    elif ch == ' ':
        reset()
        toggleEmergencyMode()
    else:
        print ("Invalid command!")

'''
    elif ch == '+':
        increaseSpeed()
    elif ch == '-':
        decreaseSpeed()
'''