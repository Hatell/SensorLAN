#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8

import argparse
import codecs
import sys

from datetime import datetime
from decimal import Decimal

from SensorLAN import SensorLAN, \
                      SensorXML, \
                      SensorSocketUDP, \
                      SensorSocketDebug


parser = argparse.ArgumentParser("OneWire Sensors")

parser.add_argument(
  "--devices",
  default="devices",
  help="Device list, contains lines '<ID>: <Name>'",
)
parser.add_argument(
  "--debug",
  default=False,
  action="store_true",
  help="Debug mode",
)
parser.add_argument(
  "--w1-dir",
  default="/sys/bus/w1/devices",
  help="Path to /sys/bus/w1/devices",
)
parser.add_argument(
  "--status",
  default=False,
  action="store_true",
  help="Check status and exit",
)

args = parser.parse_args()

def parseCelsius(s):
  return (Decimal(s) / Decimal("1000")).quantize(Decimal("0.001"))

devices = []

with codecs.open(args.devices, "r", "UTF-8") as f:
  for r in f:
    devices.append({
      "id": r[:15],
      "name": r[16:].strip(),
      "model": "DS18B20",
      "relative": False,
      "type": "thermal",
      "value": None,
      "unit": "celsius",
    })
  # with f

data = []

for dev in devices:
  try:
    with open(args.w1_dir + "/" + dev["id"] + "/w1_slave", "r") as f:
      lines = [r.strip() for r in f]
      if "YES" in lines[0]:
        c = lines[1][29:]
        if args.status:
          print dev["id"], dev["name"], parseCelsius(c), "OK"
        else:
          dev["value"] = str(parseCelsius(c))

          data.append(dev)
      else:
        if args.status:
          print dev["id"], dev["name"], "------ FAIL <-----------------"
  except:
    if args.status:
      print dev["id"], dev["name"], "------ FAIL <-----------------"

if len(data) == 0:
  sys.exit()

sensorLAN = None

if args.debug:
  sensorLAN = SensorLAN(
    SensorSocketDebug(),
    SensorXML(),
    None,
  )
else:
  sensorLAN = SensorLAN(
    SensorSocketUDP(),
    SensorXML(),
    None,
  )


sensorLAN.sendDict({
  "id": u"NOID",
  "time": datetime.now(),
  "Location": {
    "name": u"Veijonhovi",
    "street": u"Insinöörinkatu",
    "coords": u"FIXME",
  },
  "Sensors": data,
})


