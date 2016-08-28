#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8
#

import argparse
import socket
import pprint

from decimal import Decimal
from datetime import datetime

from SensorLAN import SensorGnuPG, SensorXML


parser = argparse.ArgumentParser()

parser.add_argument(
  "--schema",
  help="SensorLAN.xsd location",
)
parser.add_argument(
  "--SensorLANDisplay",
  action="store_true",
  default=False,
)
parser.add_argument(
  "--bind",
  help="Bind to address, default all addresses",
  default="",
)
parser.add_argument(
  "--port",
  type=int,
  help="UDP port, default 61000",
  default=61000,
)

args = parser.parse_args()

gpg = SensorGnuPG()
xml = SensorXML(args.schema)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

sock.bind((args.bind, args.port,))

DBusProxy = None

if args.SensorLANDisplay:
  import dbus
  import dbus.exceptions
  DBusProxy = dbus.SessionBus().get_object(
    "org.gnome.Shell",
    "/org/gnome/Shell/Extensions/SensorLANDisplay"
  )
  DBusSensorLANIface = dbus.Interface(
    DBusProxy,
    "org.gnome.Shell.Extensions.SensorLANDisplay"
  )


while True:
  (readData, fromAddr,) = sock.recvfrom(4092)
  signed = gpg.isSigned(readData)
  valid = False

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

  print "Read %d from %s, %d" % (len(readData), fromAddr[0], fromAddr[1])

  if not valid:
    print "Data wasn't valid"
    if gpg is not None and gpg.keyMissing:
      print "Key is missing"

    continue

  if valid and DBusProxy is not None:
    d = xml.parse(data)

    try:
      DBusSensorLANIface.Display(
        ", ".join([
          "%s %.1f" % (s["name"], Decimal(s["value"]),) for s in d["Sensors"]
        ]) + " (%s)" % (datetime.now().strftime("%H.%M"),)
      )
    except dbus.exceptions.DBusException as e:
      print e
      print "Exception"
      pass
    except TypeError:
      pass


