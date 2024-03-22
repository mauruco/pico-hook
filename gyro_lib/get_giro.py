from gyro_lib.imu import MPU6050
from time import sleep
from machine import Pin, I2C
from machine import Pin

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
imu = MPU6050(i2c)
led = Pin(25, Pin.OUT)

while True:
  # led.toggle()
  ax=imu.accel.x
  ay=imu.accel.y
  az=imu.accel.z
  gx=imu.gyro.x + 5.686467
  gy=imu.gyro.y + 14.68681
  gz=imu.gyro.z + 8.847534
  # tem=imu.temperature
  print("#ax" + str(ax) +"#ay" + str(ay) + "#az" + str(az) + "#gx" + str(gx) + "#gy" + str(gy) + "#gz" + str(gz) + "#")
  sleep(0.001)

