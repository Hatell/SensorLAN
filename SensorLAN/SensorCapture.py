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

args = parser.parse_args()

gpg = SensorGnuPG()
xml = SensorXML(args.schema)
sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)

sock.bind(("", args.udp,))

while True:
  (readData, fromAddr,) = sock.recvfrom(4092)
  signed = gpg.isSigned(readData)
  valid = False

  print "Read %d from %s, %d" % (len(readData), fromAddr[0], fromAddr[1])
  if signed:
    print readData
    data = gpg.verify(readData)
  else:
    data = readData

  if data is not None:
    valid = True

  try:
    pprint.pprint(xml.parse(data))

    if signed and not valid:
      print "Data is invalid signed"
    elif not signed:
      print "Data wasn't signed"
  except:
    valid = False

  if not valid:
    print "Data wasn't valid"
    if gpg is not None and gpg.keyMissing:
      print "Key is missing"
  else:
    print "Data was good"
  print

