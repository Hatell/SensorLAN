#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8
#

import argparse
import pprint

from socket import *
from impacket import ImpactPacket

from SensorLAN import SensorLAN, SensorGnuPG, SensorXML, SensorSocketEthernet


parser = argparse.ArgumentParser()

parser.add_argument(
  "--schema",
  help="SensorLAN.v1.xsd schema location",
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
  "ifname",
)
parser.add_argument(
  "file",
  type=argparse.FileType("r"),
)

args = parser.parse_args()

sensorSock = SensorSocketEthernet(args.ifname, args.port, args.no_ip)
sensorXML = SensorXML(args.schema)
sensorXML.parse(args.file.read())
sensorGPG = None

dataStr = None

if args.gpg_key is not None:
  gpg = SensorGnuPG(args.gpg_key)

sensorLAN = SensorLAN(sensorSock, sensorXML, sensorGPG)

sensorLAN.send()

