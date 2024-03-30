from _thread import start_new_thread
from os import stat
from sys import exit
from machine import Pin
from rp2 import bootsel_button
from json import loads
from utime import sleep

led = Pin(25, Pin.OUT)
led.off()

# wait for calibration input
sleep(3)

# calibration if bootsel button is pressed
if bootsel_button():
  from calibrate import CALIBRATE
  from machine import reset, I2C
  from mpu6050 import MPU6050

  # init mpu
  i2c = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
  mpu6050 = MPU6050(0x68, i2c)

  # calibration
  offsets = CALIBRATE(mpu6050).start()

  # very fast blink indicates calibration failed
  if offsets == False:
    exit()

  # save offsets
  with open('offsets.json', 'w') as f:
    f.write(loads(offsets))
  print('Calibration Done')
  reset()

# startup done
led.on()

# helper
def file_exists(filename):
  try:
    stat(filename)
    return True
  except OSError:
    return False

# init data
ax, ay, az, gx, gy, gz = 0, 0, 0, 0, 0, 0
def get_data():
  global ax, ay, az, gx, gy, gz
  return ax, ay, az, gx, gy, gz


def core1_thread():
  from machine import I2C
  from utime import sleep
  from mpu6050 import MPU6050

  # init mpu
  i2c = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
  mpu6050 = MPU6050(0x68, i2c)

  global ax, ay, az, gx, gy, gz

  # load offsets
  offsets = {'ax': 0, 'ay': 0, 'az': 0, 'gx': 0, 'gy': 0, 'gz': 0}
  if file_exists('offsets.json'):
    with open('offsets.json', 'r') as f:
      offsets = loads(f.read())

  while True:
    ax, ay, az, gx, gy, gz = mpu6050.get_acc_gyro(offsets['ax'], offsets['ay'], offsets['az'], offsets['gx'], offsets['gy'], offsets['gz'])
    # sleep(0.001)

# core 0
def core0_thread():
  from cemu import CEMU
  from udp_server import UDPSERVER
  from wifi import connect

  global ax, ay, az, gx, gy, gz

  # wifi
  if not file_exists('config.json'):
    print('config.json not found')
    exit()

  config = {}
  with open('config.json', 'r') as f:
    config = loads(f.read())

  # wifi
  _, mac = connect(config['wifiSsid'], config['wifiPass'])

  # init CEMU
  cemu = CEMU()

  # server
  server = UDPSERVER()
  server.listen(mac, config['serverId'], config['activeSlot'], cemu.make_info_response, cemu.make_data_response, get_data)

# Start the core1 thread
start_new_thread(core1_thread, ())

# Run the main function
core0_thread()
