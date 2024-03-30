import usocket
import uselect

class UDPSERVER:
  def __init__(self):
    self.sock = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
    self.sock.setblocking(False)
    self.sock.bind(('0.0.0.0', 26760))

  def listen(self, mac, serverId, activeSlot, make_info_response, make_data_response, get_data):
    p = uselect.poll()
    p.register(self.sock, uselect.POLLIN)
    to = 0 # wait for ms

    eventType1Addr = False
    eventType2Addr = False
    amountSlots = 1 # max 4
    currentSlot = 0
    while True:
      if p.poll(to):
          data, addr = self.sock.recvfrom(17)

          # controller info
          if data[16] == 1:
            eventType1Addr = addr
            if data[20] > amountSlots:
              amountSlots = 4 if data[20] > 4 else data[20]

          # controller data
          if data[16] == 2:
            eventType2Addr = addr

      # always send info/data response
      # we send one slot at a time to not block the loop with 4 controllerInfo packets at once
      if eventType1Addr:
        info = make_info_response(mac, serverId, activeSlot, currentSlot)
        self.sock.sendto(info, eventType1Addr) # blocking
        currentSlot += 1
        if currentSlot >= amountSlots:
          currentSlot = 0
          # reset after sending all slots, wait for next controllerInfo packet
          eventType1Addr = False

      # we always send controller data
      if eventType2Addr:
        ax, ay, az, gx, gy, gz = get_data()
        data0 = make_data_response(mac, serverId, activeSlot, ax, ay, az, gx, gy, gz)
        self.sock.sendto(data0, eventType2Addr)  # blocking

