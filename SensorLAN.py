#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8
#

from SensorSocket import SensorSocket
from SensorXML import SensorXML
from SensorGnuPG import SensorGnuPG

class SensorLAN(object):
  def __init__(self, sensorSocket, sensorXML, sensorGnuPG):
    super(SensorLAN, self).__init__()

    if not isinstance(sensorSocket, SensorSocket):
      raise TypeError("sensorSocket")

    if not isinstance(sensorXML, SensorXML):
      raise TypeError("sensorXML")

    if sensorGnuPG is not None and not isinstance(sensorGnuPG, SensorGnuPG):
      raise TypeError("sensorGnuPG")

    self.sensorSocket = sensorSocket
    self.sensorXML = sensorXML
    self.sensorGnuPG = sensorGnuPG
    pass # def __init__

  def sendDict(self, d):
    self.sensorXML.fromDict(d)

    self.send()
    pass # def sendDict

  def send(self):
    data = self.sensorXML.toStr()

    if self.sensorGnuPG is not None:
      data = self.sensorGnuPG.sign(data)

    self.sensorSocket.sendto(data)
    pass # def send

  pass # class SensorLAN

