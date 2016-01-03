#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8
#

import argparse

from SensorLAN import SensorXML


parser = argparse.ArgumentParser()
parser.add_argument(
  "--schema",
  help="SensorLAN xsd schema",
)
parser.add_argument(
  "file",
  type=argparse.FileType("rb"),
)

args = parser.parse_args()


xml = SensorXML(args.schema)
xml.parse(args.file.read())
print "Valid"
