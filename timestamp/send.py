#!/usr/bin/env python3
import argparse
import sys
import socket
import random
import struct
import argparse

from scapy.all import sendp, send, get_if_list, get_if_hwaddr, hexdump
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP, Raw

def main():
    
    iface = 'veth7'

    print(("sending on interface %s" % iface))
    pkt =  Ether(src='22:22:22:22:22:22', dst='11:11:11:11:11:11')
    pkt = pkt /IP(src='1.2.3.4', dst='100.99.98.97') / UDP(dport=0xabcd, sport=0x1234) / Raw(load='\x00'*58)
    
    pkt.show2()
#    hexdump(pkt)
#    print "len(pkt) = ", len(pkt)
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
