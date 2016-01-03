#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8
#

from lxml import etree
from datetime import datetime


class SensorXML(object):
  """SensorXML handles XML to dict and dict to XML conversions.

Validates data when read.
"""


  def __init__(self, schemaFile=None):
    """SensorXML = SensorXML(schemaFile=None)

If schemaFile is None then objects uses internal xsd schema, SensorLAN.v1.xsd
"""
    super(SensorXML, self).__init__()

    self.schema = None
    self.doc = None

    if schemaFile is not None:
      self.schema = etree.XMLSchema(etree.parse(schemaFile))
    else:
      import os
      self.schema = etree.XMLSchema(etree.parse(os.path.join(
        os.path.dirname(
          os.path.abspath(__file__),
        ),
        "..",
        "xsd",
        "SensorLAN.v1.xsd",
      )))

    # def __init__


  def parse(self, data):
    """dict = SensorLAN(data)

Data must be raw xml-data.
"""
    self.doc = etree.fromstring(data)
    self.validate()

    return self.toDict()
    # def parse


  def validate(self):
    """None = SensorXML.validate()

Validates data in memory.
"""
    if self.schema is None:
      return

    self.schema.assertValid(self.doc)

    # def validate


  def toDict(self):
    """dict|None = SensorXML.toDict()

Return None if no data, otherwise returns dict.
"""
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
        "relative": s.get("relative").lower() == "true",
        "name": s.get("name"),
        "model": s.get("model"),
        "type": s.get("type"),
        "value": s.xpath("Value")[0].text,
        "unit": s.xpath("Value")[0].get("unit"),
        } for s in self.doc.xpath("/SensorLAN/Sensor")
      ]
    }
    return d
    # def toDict


  def fromDict(self, d):
    """None = SensorXML(d)

Loads data from given dict (d) to memory.
"""
    from . import ElementsSensorLAN as SL

    sensors = [
      SL.Sensor({
        "id": s["id"],
        "name": s["name"],
        "model": s["model"],
        "type": s["type"],
        "relative": str(s["relative"]).lower(),
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
    # def fromDict


  def toStr(self, pretty_print=True):
    """str|None = SensorXML.toStr(pretty_print=True)

Return None if no data, otherwise returns raw xml-data.
"""
    if self.doc is None:
      return None

    return etree.tostring(
      self.doc,
      xml_declaration=True,
      encoding="utf-8",
      pretty_print=pretty_print
    )
    # def toStr


  # class SensorXML


