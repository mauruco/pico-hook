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
    while True:
      if bootsel_button() and not ax:
        sleep(0.5)
        # calibrate_accel, rotate MPU 90 degrees in X or Y axis
        self.timer.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:self.led.toggle())
        print('Starting Accel Calibration X')
        self.timer.deinit()
        self.led.off()
        self.timer.init(period=100, mode=Timer.PERIODIC, callback=lambda t:self.led.toggle())
        self.offsets.update(self.mpu6050.calibrate_accel())
        self.timer.deinit()
        self.led.on()
        print('X axis calibration done: ', self.offsets)
        ax = True

      if not ax:
        continue

      if bootsel_button() and not ay:
        sleep(0.5)
        # calibrate_accel, rotate MPU 90 degrees, if you rotated in X axis, rotate in Y axis now, vice versa
        self.timer.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:self.led.toggle())
        print('Starting Accel Calibration Y')
        self.timer.deinit()
        self.led.off()
        self.timer.init(period=100, mode=Timer.PERIODIC, callback=lambda t:self.led.toggle())
        self.offsets.update(self.mpu6050.calibrate_accel())
        self.timer.deinit()
        self.led.on()
        print('Y axis calibration done: ', self.offsets)
        ay = True

      if not ay:
        continue

      if bootsel_button() and not az:
        sleep(0.5)
        # calibrate_accel Z
        self.timer.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:self.led.toggle())
        print('Starting Accel Calibration Z')
        self.timer.deinit()
        self.led.off()
        self.timer.init(period=100, mode=Timer.PERIODIC, callback=lambda t:self.led.toggle())
        self.offsets.update(self.mpu6050.calibrate_accel())
        self.timer.deinit()
        self.led.on()
        print('Z axis calibration done: ', self.offsets)
        az = True
      
      if not az:
        continue

      if bootsel_button() and not gxyz:
        sleep(0.5)
        # calibrate_gyro
        self.timer.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:self.led.toggle())
        print('Starting Gyro Calibration X Y Z')
        self.timer.deinit()
        self.led.off()
        self.timer.init(period=100, mode=Timer.PERIODIC, callback=lambda t:self.led.toggle())
        self.offsets.update(self.mpu6050.calibrate_gyro())
        self.timer.deinit()
        self.led.on()
        print('Gyro calibration done: ', self.offsets)
        gxyz = True

      if ax and ay and az and gxyz:
        break

    print(self.offsets)

    if 'ax' in self.offsets and 'ay' in self.offsets and 'az' in self.offsets and 'gx' in self.offsets and 'gy' in self.offsets and 'gz' in self.offsets:
      self.led.off()
      print('Calibration Successful')
      return self.offsets
    else:
      self.timer.init(period=50, mode=Timer.PERIODIC, callback=lambda t:self.led.toggle())
      print('Calibration Failed')
      return False