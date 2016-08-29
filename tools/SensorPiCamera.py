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
  "--preview-only",
  default=False,
  action="store_true",
)
parser.add_argument(
  "--camera-resolution",
  type=lambda s: map(int, s.split("x")),
)
parser.add_argument(
  "--camera-preview",
  type=int,
  default=10,
  help="Preview only x seconds",
)
parser.add_argument(
  "--camera-preview-alpha",
  type=int,
  default=220,
  help="value between 0 and 255",
)
parser.add_argument(
  "--camera-awb-mode",
)
parser.add_argument(
  "--camera-exposure-mode",
  help="https://www.raspberrypi.org/learning/getting-started-with-picamera/worksheet/",
)
parser.add_argument(
  "--image-rotate",
  type=int,
  help="degree counter-clockwise",
)
parser.add_argument(
  "--image-convert",
  type=int,
  help="Number of colors",
)
parser.add_argument(
  "--image-convert-dither",
  default=False,
  action="store_true",
  help="Use default dithering",
)
parser.add_argument(
  "--image-crop",
  type=lambda s: map(int, s.split(",")),
  help="LEFT,TOP,RIGHT,BOTTOM",
)
parser.add_argument(
  "--tesseract-config",
  default="-psm 6 digits",
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

if args.camera_resolution:
  camera.resolution = args.camera_resolution

if args.camera_exposure_mode:
  camera.exposure_mode = args.camera_exposure_mode

if args.camera_awb_mode:
  camera.awb_mode = args.camera_awb_mode

dst = "/tmp/SensorLANPiCamera.jpg"
camera.start_preview(alpha=args.camera_preview_alpha)

sleep(args.camera_preview)

if args.preview_only:
  camera.stop_preview()
  sys.exit()

camera.capture(dst)
camera.stop_preview()

value = None

if args.image_convert:
  convert_dst = "%s_convert.jpg" % dst.split(".")[0]

  with Image.open(dst) as img:

    convert_img = img.convert(
      "P",
      dither=None if args.image_convert_dither else Image.NONE,
      palette=Image.ADAPTIVE,
      colors=args.image_convert,
    )
    convert_img.save(convert_dst)

  dst = convert_dst

if args.image_rotate:
  rotate_dst = "%s_rotate.jpg" % dst.split(".")[0]

  with Image.open(dst) as img:

    rotate_img = img.rotate(args.image_rotate)
    rotate_img.save(rotate_dst)

  dst = rotate_dst

if args.image_crop:
  crop_dst = "%s_crop.jpg" % dst.split(".")[0]

  with Image.open(dst) as img:

    crop_img = img.crop(args.image_crop)
    crop_img.save(crop_dst)

  dst = crop_dst

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

