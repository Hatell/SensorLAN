#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8
#

import argparse
import pprint

from socket import *

from SensorGnuPG import SensorGnuPG
from SensorXML import SensorXML

parser = argparse.ArgumentParser()

parser.add_argument(
  "--schema",
  default="./xsd/SensorLAN.v1.xsd",
  help="FIXME",
)
parser.add_argument(
  "--udp",
  type=int,
  help="UDP port",
  required=True,
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

gpg = SensorGnuPG()
xml = SensorXML(args.schema)
xml.parse(args.file.read())

sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

if args.gpg_key is not None:
  data = gpg.sign(args.gpg_key, xml.toStr())
else:
  data = xml.toStr()

sock.sendto(data, ("<broadcast>", args.udp,))
sock.close()
