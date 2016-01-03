#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8
#

from socket import *


class SensorSocket(object):
  def __init__(self):
    self.sock = None
    # def __init__


  def sendto(self, data):
    self.sock.sendto(self.frame(data), self.address())
    # def sendto


  pass # class SensorSocket


class SensorSocketUDP(SensorSocket):
  def __init__(self, port = 61000, addr = "<broadcast>"):
    super(SensorSocketUDP, self).__init__()
    self.sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    self.sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    self.port = port
    self.addr = addr
    pass # def __init__


  def frame(self, data):
    return data
    # def frame


  def address(self):
    return (self.addr, self.port,)
    # def address


  pass # class SensorSocketUDP


class SensorSocketEthernet(SensorSocket):
  def __init__(self, ifname, port = 61000, no_ip = False):
    super(SensorSocketEthernet, self).__init__()
    self.sock = socket(AF_PACKET, SOCK_RAW)
    self.ifname = ifname
    self.port = port
    self.no_ip = no_ip
    # def __init__


  def frame(self, data):
    from impacket import ImpactPacket

    # Ethernet
    ether = ImpactPacket.Ethernet()
    ether.set_ether_dhost((0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF))

    # IP
    ip = ImpactPacket.IP()
    ip.set_ip_dst("255.255.255.255")

    # UDP
    udp = ImpactPacket.UDP()
    udp.set_uh_dport(self.port)

    # Data
    data_packet = ImpactPacket.Data(data)

    udp.contains(data_packet)

    if self.no_ip:
      ether.contains(udp)
    else:
      ip.contains(udp)
      ether.contains(ip)

    return ether.get_packet()
    # def frame


  def address(self):
    return (self.ifname, 0,)
    # def address


  pass # class SensorSocketEthernet


class SensorSocketDebug(SensorSocket):
  def sendto(self, data):
    print data
    # def sendto


  pass  # class SensorSocketDebug
