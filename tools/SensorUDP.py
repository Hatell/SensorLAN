#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8
#

import argparse
import pprint

from SensorLAN import SensorLAN, SensorGnuPG, SensorXML, SensorSocketUDP


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

sensorSock = SensorSocketUDP(args.port, args.addr)

sensorGPG = None
sensorXML = SensorXML(args.schema)
sensorXML.parse(args.file.read())

if args.gpg_key is not None:
  sensorGPG = SensorGnuPG(args.gpg_key)

sensorLAN = SensorLAN(sensorSock, sensorXML, sensorGPG)

sensorLAN.send()
