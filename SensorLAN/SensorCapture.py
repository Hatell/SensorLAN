#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8
#

import argparse
import pprint

from decimal import Decimal
from datetime import datetime
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
  "--SensorLANDisplay",
  action="store_true",
  default=False,
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

DBusProxy = None

if args.SensorLANDisplay:
  import dbus
  DBusProxy = dbus.SessionBus().get_object(
    "org.gnome.Shell",
    "/org/gnome/Shell/Extensions/SensorLANDisplay"
  )
  DBusSensorLANIface = dbus.Interface(
    DBusProxy,
    "org.gnome.Shell.Extensions.SensorLANDisplay"
  )
  DBusSensorLANIface.Display(u"Ready")

while True:
  (readData, fromAddr,) = sock.recvfrom(4092)
  signed = gpg.isSigned(readData)
  valid = False

  print "Read %d from %s, %d" % (len(readData), fromAddr[0], fromAddr[1])
  if signed:
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

    continue

  if valid and DBusProxy is not None:
    d = xml.parse(data)

    DBusSensorLANIface.Display(", ".join([
        "%s %.1f" % (s["name"], Decimal(s["value"]),) for s in d["Sensors"]
      ]) + " (%s)" % (datetime.now().strftime("%H.%M"),)
    )

