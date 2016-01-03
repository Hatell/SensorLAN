#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8
#

import argparse
import pprint

import socket

from SensorLAN import SensorGnuPG, SensorXML


parser = argparse.ArgumentParser()

parser.add_argument(
  "--schema",
  help="SensorLAN.v1.xsd schema location.",
)
parser.add_argument(
  "--port",
  type=int,
  help="UDP port",
  default=61000,
)
parser.add_argument(
  "--addr",
  default="<broadcast>",
  help="Address to send, default <broadcast>",
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

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

if args.gpg_key is not None:
  data = gpg.sign(xml.toStr(), args.gpg_key)
else:
  data = xml.toStr()

sock.sendto(data, (args.addr, args.port,))
sock.close()
