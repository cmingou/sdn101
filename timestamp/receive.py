#!/usr/bin/env python3
import sys
import struct
import os
import logging

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr
from scapy.all import Packet, IPOption
from scapy.all import ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.all import IP, TCP, UDP
from scapy.layers.inet import _IPOption_HDR

def handle_pkt(pkt):
    print("got a packet")
    # pkt.show2()
    ts_ingress_mac, ts_ingress_global, \
        ts_enqueue, ts_dequeue_delta, \
        ts_egress_global, ts_egress_tx = \
        struct.unpack("!QQIIQQxxxxxxxxxxxxxxxxxx", str(pkt[0])[-58:])

    ns = 1000000000.0
    print("Timestamps")
    print("  raw values in ns:")
    print("    ingress mac                   : {:>15}".format(ts_ingress_mac))
    print("    ingress global                : {:>15}".format(ts_ingress_global))
    print("    traffic manager enqueue       : {:>15}".format(ts_enqueue))
    print("    traffic manager dequeue delta : {:>15}".format(ts_dequeue_delta))
    print("    egress global                 : {:>15}".format(ts_egress_global))
    print("    egress tx (no value in model) : {:>15}".format(ts_egress_tx))
    print("  values in s:")
    print("    ingress mac                   : {:>15.9f}".format(ts_ingress_mac / ns))
    print("    ingress global                : {:>15.9f}".format(ts_ingress_global / ns))
    print("    traffic manager enqueue       : {:>15.9f}".format(ts_enqueue / ns))
    print("    traffic manager dequeue delta : {:>15.9f}".format(ts_dequeue_delta / ns))
    print("    egress global                 : {:>15.9f}".format(ts_egress_global / ns))
    print("    egress tx (no value in model) : {:>15.9f}".format(ts_egress_tx))
    print("Please note that the timestamps are using the internal time " +
                "of the model/chip. They are not synchronized with the global time. "
                "Furthermore, the traffic manager timestamps in the model do not " +
                "accurately reflect the packet processing. Correct values are shown " +
                "by the hardware implementation.")

    sys.stdout.flush()

def main():
    iface = 'veth9'
    print(("sniffing on %s" % iface))
    sys.stdout.flush()
    sniff(iface = iface,
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
