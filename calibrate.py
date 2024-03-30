from time import sleep
from machine import Pin, Timer
from rp2 import bootsel_button

class CALIBRATE:
  def __init__(self, mpu6050):
    self.offsets = {}
    self.mpu6050 = mpu6050
    self.led = Pin(25, Pin.OUT)
    self.timer = Timer(-1)
    self.led.off()
    print('Settling MPU for 5 seconds')
    sleep(5)
    print('MPU is Done Settling')
    self.led.on()

  def start(self):
    ax, ay, az, gxyz = False, False, False, False

    # slow blink indicates ready for calibration
    self.timer.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:self.led.toggle())

    while True:
      if bootsel_button() and not ax:
        self.timer.deinit()
        self.led.off()
        sleep(0.5)
        # calibrate_accel, rotate MPU 90 degrees in X or Y axis
        print('Starting Accel Calibration X')
        self.offsets.update(self.mpu6050.calibrate_accel())
        print('X axis calibration done: ', self.offsets)
        ax = True
        # slow blink indicates ready for calibration
        self.timer.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:self.led.toggle())

      if not ax:
        continue

      if bootsel_button() and not ay:
        self.timer.deinit()
        self.led.off()
        sleep(0.5)
        # calibrate_accel, rotate MPU 90 degrees, if you rotated in X axis, rotate in Y axis now, vice versa
        print('Starting Accel Calibration Y')
        self.offsets.update(self.mpu6050.calibrate_accel())
        print('Y axis calibration done: ', self.offsets)
        ay = True
        # slow blink indicates ready for calibration
        self.timer.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:self.led.toggle())

      if not ay:
        continue

      if bootsel_button() and not az:
        self.timer.deinit()
        self.led.off()
        sleep(0.5)
        # calibrate_accel Z
        print('Starting Accel Calibration Z')
        self.offsets.update(self.mpu6050.calibrate_accel())
        print('Z axis calibration done: ', self.offsets)
        az = True
        # slow blink indicates ready for calibration
        self.timer.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:self.led.toggle())
      
      if not az:
        continue

      if bootsel_button() and not gxyz:
        self.timer.deinit()
        self.led.off()
        sleep(0.5)
        # calibrate_gyro
        print('Starting Gyro Calibration X Y Z')
        self.offsets.update(self.mpu6050.calibrate_gyro())
        print('Gyro calibration done: ', self.offsets)
        gxyz = True
        # slow blink indicates ready for calibration
        self.timer.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:self.led.toggle())

      if ax and ay and az and gxyz:
        break

    if 'ax' in self.offsets and 'ay' in self.offsets and 'az' in self.offsets and 'gx' in self.offsets and 'gy' in self.offsets and 'gz' in self.offsets:
      self.timer.deinit()
      self.led.off()
      print('Calibration Successful')
      return self.offsets
    else:
      self.timer.deinit()
      # fast blink indicates calibration failed
      self.timer.init(period=100, mode=Timer.PERIODIC, callback=lambda t:self.led.toggle())
      print('Calibration Failed')
      return False
    
from mpu6050 import MPU6050
from machine import I2C, Pin
# init mpu
i2c = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
mpu6050 = MPU6050(0x68, i2c)

# CALIBRATE(mpu6050).start()

while True:
  offx, offy, offz = 0.05833888, -0.01418775, 0.03186357
  ax, ay, az = mpu6050.read_accel_raw()

  print('Accel X: ', az - (offz))