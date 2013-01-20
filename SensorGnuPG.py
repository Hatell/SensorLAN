#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8
#
#

import re
import GnuPGInterface

from SensorXML import SensorXML

class SensorGnuPG(GnuPGInterface.GnuPG):

  def __init__(self):
    GnuPGInterface.GnuPG.__init__(self)

    pass # def __init__

  def sign(self, keyID, unsignedbytes):
    """
Sign given data and return signedbytes

signdesbytes = sign(key, bytes)

On error returns None
"""
    signedbytes = None

    try:
      proc = self.run(
        ["--clearsign", "-u", keyID],
        create_fhs=["stdin", "stdout"]
      )

      proc.handles["stdin"].write(unsignedbytes)
      proc.handles["stdin"].close()

      signedbytes = proc.handles["stdout"].read()
      proc.handles["stdout"].close()

      proc.wait()
    except IOError as e:
      pass

    return signedbytes
    pass # def sign

  def isSigned(self, data):
    """
Returns True if data is signed otherwise False

bool = isSigned(data)
"""

    if not hasattr(type(data), "startswith"):
      return False

    return data.startswith("-----BEGIN PGP SIGNED MESSAGE-----")
    pass # def isSigned

  def verify(self, signedbytes):
    """
Verify signed bytes and return signed data

data = verify(signedbytes)

On error returns None
"""
    data = None

    proc = self.run(
      ["--decrypt", "--output", "-"],
      create_fhs=["stdin", "stdout", "stderr"]
    )

    try:
      proc.handles["stdin"].write(signedbytes)
      proc.handles["stdin"].close()

      data = proc.handles["stdout"].read()
      proc.handles["stdout"].close()

      # Pick sign key id
      m = re.search("key ID ([0-9A-F]{8})", proc.handles["stderr"].read())

      keyId = m.group(1)

      proc.wait()
    except IOError as e:
      pass

    # Check if SensorLAN attribute id is same as key which is used to sign data
    # Doesn't need XMLSchema validation
    try:
      xml = SensorXML()

      xml.parse(data)

      if len(xml.doc.xpath("/SensorLAN[@id = $keyId]", keyId = keyId)) != 1:
        return None
    except:
      return None

    return data
    pass # def verify
  pass # class SensorGnuPG
