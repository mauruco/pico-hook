from _thread import start_new_thread
from os import stat
from sys import exit
from json import loads
from socket import socket, AF_INET, SOCK_DGRAM
from time import sleep, time
from rp2 import bootsel_button
from machine import Pin, I2C, Timer
from wifi import connect
from cemu import CEMU
from mpu6050 import MPU6050

# helper
def file_exists(filename):
  try:
    stat(filename)
    return True
  except OSError:
    return False

# wifi
if not file_exists('wifi-config.json'):
  print('wifi-config.json not found')
  exit()

wifiConfig = {}
with open('wifi-config.json', 'r') as f:
  wifiConfig = loads(f.read())

# wait
sleep(2)

# init mpu
i2c = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
mpu6050 = MPU6050(0x68, i2c)

# init data
ax, ay, az, gx, gy, gz = 0, 0, 0, 0, 0, 0

# init CEMU
cemu = CEMU()

# check if the button is pressed, enter the calibration mode
if bootsel_button():
  from calibrate import CALIBRATE
  from sys import exit
  offsets = CALIBRATE(mpu6050).start()
  if offsets == False:
    print('Calibration Failed')
    exit()
  # save offsets
  with open('offsets.json', 'w') as f:
    f.write(loads(offsets))
  print('Calibration Done')
  exit()

# load offsets
offsets = {'ax': 0, 'ay': 0, 'az': 0, 'gx': 0, 'gy': 0, 'gz': 0}
if file_exists('offsets.json'):
  with open('offsets.json', 'r') as f:
    offsets = loads(f.read())

# core 0
def core0_thread():
  global ax, ay, az, gx, gy, gz

  led = Pin(25, Pin.OUT)
  led.off()
  timer = Timer(-1)
  timer.init(period=100, mode=Timer.PERIODIC, callback=lambda t:led.toggle())

  # wifi
  connect(wifiConfig['ssid'], wifiConfig['password'])

  # Create a new UDP socket
  s = socket(AF_INET, SOCK_DGRAM)

  # Bind the socket to a specific address and port
  s.bind(('0.0.0.0', 26760))  # Use your desired port number
  
  # wait for event1, ryujinx do not send event1
  wait = time()

  def sendInfoResponse(s, addr):
    info0 = cemu.make_info_response(0)
    # info1 = make_info_response(1)
    # info2 = make_info_response(2)
    # info3 = make_info_response(3)
    s.sendto(info0, addr)
    # s.sendto(info1, addr)
    # s.sendto(info2, addr)
    # s.sendto(info3, addr)

  # resend eventtype 1 every x seconds
  msCounter = 0.0

  # info and data address destination
  eventType1Addr = 0
  eventType2Addr = 0

  while True:        
    # Receive up to 1024 bytes from the client
    data, addr = s.recvfrom(32)
    print('eventtype', data[16])

    if data[16] == 1: # controller info
      eventType1Addr = addr
      sendInfoResponse(s, eventType1Addr)

    if data[16] == 2: # controller data
      eventType2Addr = addr

    # wait 5 seconds for event1, ryujinx do not send event1
    if eventType1Addr == 0 and eventType2Addr != 0:
      now = time.time()
      if now - wait < 5:
        continue

    if eventType2Addr != 0:

      # stop timer, led on indicating success
      timer.deinit()
      led.on()

      while True:
        # exit loop if boot button is pressed reconnect to client
        if bootsel_button():
          eventType1Addr = 0
          eventType2Addr = 0
          led.off()
          timer.init(period=100, mode=Timer.PERIODIC, callback=lambda t:led.toggle())
          break

        # convert data to cemu
        dataAx, dataAy, dataAz, dataPitch, dataRoll, dataYaw = -ax, -az, ay, gx, gy, -gz
        
        # data
        data0 = cemu.make_data_response(dataAx, dataAy, dataAz, dataPitch, dataRoll, dataYaw)
        s.sendto(data0, eventType2Addr)

        # info
        # resend eventtype 1 every x seconds
        if eventType1Addr != 0:
          msCounter += 0.0001
          if msCounter > 0.001:
              msCounter = 0
              sendInfoResponse(s, eventType1Addr)

def core1_thread():
  global ax, ay, az, gx, gy, gz
  while True:
    ax, ay, az, gx, gy, gz = mpu6050.get_acc_gyro(offsets['ax'], offsets['ay'], offsets['az'], offsets['gx'], offsets['gy'], offsets['gz'])

# core2
second_thread = start_new_thread(core1_thread, ())
# core1
core0_thread()
