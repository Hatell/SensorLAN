#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8
#

from StringIO import StringIO
from lxml import etree
from datetime import datetime

import ElementsSensorLAN as SL

class SensorXML(object):
  def __init__(self, schemaFile = None):
    """FIXME"""
    super(SensorXML, self).__init__()

    self.schema = None

    if schemaFile is not None:
      self.schema = etree.XMLSchema(etree.parse(schemaFile))

    pass # def __init__

  def parse(self, data):
    """FIXME"""
    self.doc = etree.parse(StringIO(data))
    self.validate()

    return self.toDict()
    pass # def parse

  def validate(self):
    """FIXME"""
    if self.schema is None:
      return

    self.schema.assertValid(self.doc)

    pass # def validate

  def toDict(self):
    """FIXME"""
    if self.doc is None:
      return None

    l = self.doc.xpath("/SensorLAN")[0]
    i = self.doc.xpath("/SensorLAN/Location")[0]

    d = {
      "id": l.get("id"),
      "time": datetime.strptime(l.get("time"), "%Y-%m-%dT%H:%M:%S"),
      "Location": {
        "name": i.xpath("Name")[0].text,
        "street": i.xpath("Street")[0].text,
        "coords": i.xpath("Coords")[0].text,
      },
      "Sensors": [{
        "id": s.get("id"),
        "relative": s.get("relative"),
        "name": s.get("name"),
        "model": s.get("model"),
        "type": s.get("type"),
        "value": s.xpath("Value")[0].text,
        "unit": s.xpath("Value")[0].get("unit"),
        } for s in self.doc.xpath("/SensorLAN/Sensor")
      ]
    }
    return d
    pass # def toDict

  def fromDict(self, d):
    sensors = [
      SL.Sensor({
        "id": s["id"],
        "name": s["name"],
        "model": s["model"],
        "type": s["type"],
        "relative": s["relative"],
      },
      SL.Value({"unit": s["unit"]}, s["value"])
      )
      for s in d["Sensors"]
    ]

    self.doc = SL.SensorLAN({
        "id": d["id"],
        "time": d["time"].strftime("%Y-%m-%dT%H:%M:%S"),
      },
      SL.Location(
        SL.Name(d["Location"]["name"]),
        SL.Street(d["Location"]["street"]),
        SL.Coords(d["Location"]["coords"])
      ),
      *sensors
    )

    self.validate()
    pass # def fromDict


  def toStr(self, pretty_print=True):
    if self.doc is None:
      return None

    return etree.tostring(
      self.doc,
      xml_declaration=True,
      encoding="utf-8",
      pretty_print=pretty_print
    )
    pass # def toStr

  pass # class SensorXML

if __name__ == "__main__":
  xml = SensorXML("./xsd/SensorLAN.v1.xsd")

  data = None

  with open("samples/unsigned_sample.xml") as f:
    data = f.read()

  import pprint
  d = (xml.parse(data))

  d["time"] = datetime.now()

  xml.fromDict(d)
  print xml.toStr()
