import _thread
import socket
import pico_wifi.wifi as wifi
import make_response
import time
from gyro import gyro_calibration, get_gyro_data

# global
dataGyro = {'ax': 0.0, 'ay': 0.0, 'az': 0.0, 'pitch': 0.0, 'roll': 0.0, 'yaw': 0.0}


def core0_thread():
  global dataGyro

  # wifi
  wifi.connect()

  # Create a new UDP socket
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  # Bind the socket to a specific address and port
  s.bind(('0.0.0.0', 26760))  # Use your desired port number

  # resend eventtype 1 every 5 seconds
  msCounter = 0.0

  eventType1Addr = 0
  eventType2Addr = 0
  
  # wait for event1, ryujinx do not send event1
  wait = time.time()

  def sendInfoResponse(s, addr):
    info0 = make_response.makeInfoResponse(0)
    # info1 = make_response.makeInfoResponse(1)
    # info2 = make_response.makeInfoResponse(2)
    # info3 = make_response.makeInfoResponse(3)
    s.sendto(info0, addr)
    # s.sendto(info1, addr)
    # s.sendto(info2, addr)
    # s.sendto(info3, addr)

  while True:
    # Receive up to 1024 bytes from the client
    data, addr = s.recvfrom(32)
    print('eventtype', data[16])

    if data[16] == 1: # controller info
      eventType1Addr = addr
      sendInfoResponse(s, eventType1Addr)

    if data[16] == 2: # controller data
      eventType2Addr = addr

    if eventType1Addr == 0 and eventType2Addr != 0:
      now = time.time()
      if now - wait < 5:
        continue

    if eventType2Addr != 0:
      while True:
        # data
        data0 = make_response.makeDataResponse(dataGyro['ax'], dataGyro['ay'], dataGyro['az'], dataGyro['pitch'], dataGyro['yaw'], dataGyro['roll'])
        s.sendto(data0, eventType2Addr)

        # info
        # resend eventtype 1 after some time
        if eventType1Addr != 0:
          msCounter += 0.0001
          if msCounter > 0.001:
              msCounter = 0
              sendInfoResponse(s, eventType1Addr)

def core1_thread():
  global dataGyro
  # calibration of the gyroscope
  # offsets = gyro_calibration()
  while True:
    dataGyro = get_gyro_data([-6.038989, -14.0842, -8.721608])

# core2
second_thread = _thread.start_new_thread(core1_thread, ())
# core1
core0_thread()
