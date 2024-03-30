from _thread import start_new_thread
from sys import exit
from machine import Pin, reset
from rp2 import bootsel_button
from utime import sleep
from config import CONFIG
from access_point import ACCESSPOINT

config = CONFIG()
led = Pin(25, Pin.OUT)
led.off()

# wait for calibration input
sleep(3)

# enter app mode
if bootsel_button():
  ACCESSPOINT().app_mode('pico-hook', 'pico-hook')
  reset()

# calibration if forced
if config.get('forceCalibration') == 1:
  # reset
  config.set('forceCalibration', 0)
  config.save()
  
  from calibrate import CALIBRATE
  from machine import I2C
  from mpu6050 import MPU6050

  # init mpu
  i2c = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
  mpu6050 = MPU6050(0x68, i2c, config.get('gyroSensitiveRange'), config.get('accelSensitiveRange'))

  # calibration
  offsets = CALIBRATE(mpu6050).start()

  # very fast blink indicates calibration failed
  if offsets == False:
    exit()

  # save offsets
  config.set('ax', offsets['ax'])
  config.set('ay', offsets['ay'])
  config.set('az', offsets['az'])
  config.set('gx', offsets['gx'])
  config.set('gy', offsets['gy'])
  config.set('gz', offsets['gz'])
  config.save()
  reset()

# startup done
led.on()

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
  mpu6050 = MPU6050(0x68, i2c, config.get('gyroSensitiveRange'), config.get('accelSensitiveRange'))

  global ax, ay, az, gx, gy, gz

  while True:
    ax, ay, az, gx, gy, gz = mpu6050.get_acc_gyro(config.get('ax'), config.get('ay'), config.get('az'), config.get('gx'), config.get('gy'), config.get('gz'))
    # sleep(0.001)

# core 0
def core0_thread():
  from cemu import CEMU
  from udp_server import UDPSERVER
  from wifi import connect

  global ax, ay, az, gx, gy, gz

  # wifi
  ip, mac = connect(config.get('wifiSsid'), config.get('wifiPassword'))
  config.set('wifiIp', ip)
  config.save()

  # init CEMU
  cemu = CEMU()

  # server
  server = UDPSERVER()
  server.listen(mac, config.get('serverId'), config.get('activeSlot'), cemu.make_info_response, cemu.make_data_response, get_data)

# Start the core1 thread
start_new_thread(core1_thread, ())

# Run the main function
core0_thread()
