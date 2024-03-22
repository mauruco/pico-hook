# gyro data
import utime
from mpu6050 import MPU6050
import math
import time

# callibration
# MPU6050(0, 0, 1) # returns offsets

mpu = MPU6050(0, 0, 1, (-2594, 1115, 1000, 198, 465, 292)) # with offsets
 

if mpu.passed_self_test:
    while True:
      tStart=time.ticks_ms()
        # print('[{:<16}] {:<10.2f}'.format('TEMPERATURE', mpu.celsius))
        # mpu.print_data()
      ax, ay, az, gx, gy, gz = mpu.data
      pitch, roll = mpu.angles
      print(ax, ay, az, gx, gy, gz)
      print(pitch, roll)