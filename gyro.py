from gyro_lib.imu import MPU6050
from machine import Pin, I2C
from machine import Pin
import time

# i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000) # works
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=1200000) # works
imu = MPU6050(i2c)
led = Pin(25, Pin.OUT)

def get_gyro():
    gx=imu.gyro.x
    gy=imu.gyro.y
    gz=imu.gyro.z
    return gx, gy, gz

def gyro_calibration(calibration_time=10):
    print('Beginning Gyro Calibration - Do not move the MPU6050')
    # placeholder for the average of tuples in mpu_gyro_array
    offsets = [0, 0, 0]
    # placeholder for number of calculations we get from the mpu
    num_of_points = 0
    
    # We get the current time and add the calibration time
    end_loop_time = time.time() + calibration_time
    # We end the loop once the calibration time has passed
    while end_loop_time > time.time():
        num_of_points += 1
        (gx, gy, gz) = get_gyro()
        offsets[0] += gx
        offsets[1] += gy
        offsets[2] += gz
        
        # This is just to show you its still calibrating :)
        if num_of_points % 100 == 0:
            print('Still Calibrating Gyro... %d points so far' % num_of_points)
        
    print('Calibration for Gyro is Complete! %d points total' % num_of_points)
    offsets = [i/num_of_points for i in offsets] # we divide by the length to get the mean
    return offsets


def get_gyro_data(offsets):
    ax=-imu.accel.x
    ay=-imu.accel.z
    az=imu.accel.y

    pitch = -(imu.gyro.x - offsets[0])
    roll = imu.gyro.y - offsets[1]
    yaw = -(imu.gyro.z - offsets[2])

    return {'ax': ax, 'ay': ay, 'az': az, 'pitch': pitch, 'roll': roll, 'yaw': yaw}
