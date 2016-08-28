#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8

import argparse
import codecs
import sys

from datetime import datetime
from decimal import Decimal
from time import sleep
from PIL import Image

import pytesseract

from SensorLAN import SensorLAN, \
                      SensorXML, \
                      SensorSocketUDP, \
                      SensorSocketDebug

from picamera import PiCamera


parser = argparse.ArgumentParser("PiCamera OCR")

parser.add_argument(
  "--device-id",
  default="PiCamera-1",
  help="Unique id",
)
parser.add_argument(
  "--device-name",
  default="PiCamera",
  help="Device name",
)
parser.add_argument(
  "--device-model",
  default="PiCamera v1",
  help="Device name",
)
parser.add_argument(
  "--camera-awb-mode",
)
parser.add_argument(
  "--camera-exposure-mode",
  help="https://www.raspberrypi.org/learning/getting-started-with-picamera/worksheet/",
)
parser.add_argument(
  "--tesseract-config",
  default="digits",
)
parser.add_argument(
  "--debug",
  default=False,
  action="store_true",
  help="Debug mode",
)
parser.add_argument(
  "--location-name",
  default="",
)
parser.add_argument(
  "--location-street",
  default="",
)
parser.add_argument(
  "--location-coords",
  default="",
)
parser.add_argument(
  "--output",
  "-o",
  type=argparse.FileType("wb"),
)

args = parser.parse_args()

camera = PiCamera()

if args.camera_exposure_mode:
  camera.exposure_mode = args.camera_exposure_mode

if args.camera_awb_mode:
  camera.awb_mode = args.camera_awb_mode

dst = "/tmp/SensorLANPiCamera.jpg"
camera.start_preview(alpha=200)

sleep(5)
camera.capture(dst)
camera.stop_preview()

value = None

with Image.open(dst) as img:
  value = pytesseract.image_to_string(img, config=args.tesseract_config).strip()

print value

device = {
  "id": args.device_id,
  "name": args.device_name,
  "model": args.device_model,
  "relative": False,
  "type": "OCR",
  "value": value,
  "unit": "celsius",
}

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
    "name": args.location_name,
    "street": args.location_street,
    "coords": args.location_coords,
  },
  "Sensors": [device],
})

if args.output is not None:
  args.output.write(sensorLAN.sensorXML.toStr())
