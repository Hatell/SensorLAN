#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8
#

import argparse
import pprint

from socket import *
from impacket import ImpactPacket

from SensorLAN import SensorGnuPG, SensorXML


parser = argparse.ArgumentParser()

parser.add_argument(
  "--schema",
  help="SensorLAN.v1.xsd schema location",
)
parser.add_argument(
  "--ifname",
  required=True,
)
parser.add_argument(
  "--no-ip",
  action="store_true",
  default=False,
)
parser.add_argument(
  "--port",
  type=int,
  help="UDP port",
  default=61000,
)
parser.add_argument(
  "--gpg-key",
  help="GnuPG Key id",
)
parser.add_argument(
  "file",
  type=argparse.FileType("r"),
)

args = parser.parse_args()

xml = SensorXML(args.schema)
xml.parse(args.file.read())

dataStr = None

if args.gpg_key is not None:
  gpg = SensorGnuPG()
  dataStr = gpg.sign(xml.toStr(), args.gpg_key)
else:
  dataStr = xml.toStr()

sock = socket(AF_PACKET, SOCK_RAW)

# Ethernet
ether = ImpactPacket.Ethernet()
ether.set_ether_dhost((0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF))

# IP
ip = ImpactPacket.IP()
ip.set_ip_dst("255.255.255.255")

# UDP
udp = ImpactPacket.UDP()
udp.set_uh_dport(args.port)

# Data
data = ImpactPacket.Data(dataStr)

udp.contains(data)

if args.no_ip:
  ether.contains(udp)
else:
  ip.contains(udp)
  ether.contains(ip)


sock.sendto(ether.get_packet(), (args.ifname, 0,))
sock.close()
