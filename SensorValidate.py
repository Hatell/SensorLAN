#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8
#

import argparse
from lxml import etree

parser = argparse.ArgumentParser()
parser.add_argument(
  "--schema",
  default="./xsd/SensorLAN.v1.xsd",
  help="SensorLan XSD Schema",
)
parser.add_argument(
  "file",
)

args = parser.parse_args()

schemadoc = etree.parse(args.schema)

schema = etree.XMLSchema(schemadoc)

doc = etree.parse(args.file)

print schema.validate(doc)
