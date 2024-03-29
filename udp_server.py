import usocket
# import uasyncio
import uselect
from utime import ticks_ms

class UDPSERVER:
  def __init__(self):
    self.sock = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
    self.sock.setblocking(False)
    self.sock.bind(('0.0.0.0', 26760))

  def listen(self, serverId, activeSlot, make_info_response, make_data_response, get_data):
    p = uselect.poll()
    p.register(self.sock, uselect.POLLIN)
    to = 0 # wait for ms

    eventType1Addr = False
    eventType2Addr = False

    while True:
      if p.poll(to):
          data, addr = self.sock.recvfrom(17)

          # controller info
          if data[16] == 1:
            eventType1Addr = addr

          # controller data
          if data[16] == 2:
            eventType2Addr = addr

      # always send info/data response
      if eventType1Addr:
        info0 = make_info_response(serverId, activeSlot, activeSlot)
        # info1 = make_info_response(1)
        # info2 = make_info_response(2)
        # info3 = make_info_response(3)
        self.sock.sendto(info0, addr) # blocking
        # s.sendto(info1, addr)
        # s.sendto(info2, addr)
        # s.sendto(info3, addr)
        eventType1Addr = False

      if eventType2Addr:
        ax, ay, az, gx, gy, gz = get_data()
        data0 = make_data_response(serverId, activeSlot, ax, ay, az, gx, gy, gz)
        self.sock.sendto(data0, addr)  # blocking

