# import smbus
# import time
# from math import atan2, sqrt, pi

# class MPU6050:
#     MPU6050_ADDR = 0x68
#     PWR_MGMT_1 = 0x6B
#     ACCEL_XOUT_H = 0x3B
#     ACCEL_YOUT_H = 0x3D
#     ACCEL_ZOUT_H = 0x3F

#     def __init__(self, bus_number=1):
#         self.bus = smbus.SMBus(bus_number)
#         self.init_mpu6050()

#     def init_mpu6050(self):
#         self.bus.write_byte_data(self.MPU6050_ADDR, self.PWR_MGMT_1, 0)

#     def read_word_2c(self, addr):
#         high = self.bus.read_byte_data(self.MPU6050_ADDR, addr)
#         low = self.bus.read_byte_data(self.MPU6050_ADDR, addr + 1)
#         val = (high << 8) + low
#         if val >= 0x8000:
#             return -((65535 - val) + 1)
#         else:
#             return val

#     def get_accel_data(self):
#         acc_x = self.read_word_2c(self.ACCEL_XOUT_H)
#         acc_y = self.read_word_2c(self.ACCEL_YOUT_H)
#         acc_z = self.read_word_2c(self.ACCEL_ZOUT_H)
#         return acc_x, acc_y, acc_z

#     def calculate_roll_pitch(self, acc_x, acc_y, acc_z):
#         roll = atan2(acc_y, acc_z) * 180 / pi
#         pitch = atan2(-acc_x, sqrt(acc_y * acc_y + acc_z * acc_z)) * 180 / pi
#         return roll, pitch

#     def run(self, delay=0.5):
#         while True:
#             acc_x, acc_y, acc_z = self.get_accel_data()
#             roll, pitch = self.calculate_roll_pitch(acc_x, acc_y, acc_z)
#             print(f"Xacc: {acc_x}, Yacc: {acc_y}, realRoll: {roll:.2f}, realPitch: {pitch:.2f}")
#             time.sleep(delay)

# if __name__ == "__main__":
#     mpu = MPU6050()
#     mpu.run()


'''
        Read Gyro and Accelerometer by Interfacing Raspberry Pi with MPU6050 using Python
	http://www.electronicwings.com
'''
import smbus					#import SMBus module of I2C
from time import sleep          #import

#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
sleep(1) #wait here to avoid 121 IO Error

Device_Address = 0x68   # MPU6050 device address

def MPU_Init():
	#write to sample rate register
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
	
	#Write to power management register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
	
	#Write to Configuration register
	bus.write_byte_data(Device_Address, CONFIG, 0)
	
	#Write to Gyro configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
	#Write to interrupt enable register
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)
      

def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
    
        #concatenate higher and lower value
        value = ((high << 8) | low)
        
        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value




MPU_Init()

print (" Reading Data of Gyroscope and Accelerometer")

while True:

        #Read Accelerometer raw value
        acc_x = read_raw_data(ACCEL_XOUT_H)
        acc_y = read_raw_data(ACCEL_YOUT_H)
        acc_z = read_raw_data(ACCEL_ZOUT_H)
        
        #Read Gyroscope raw value
        gyro_x = read_raw_data(GYRO_XOUT_H)
        gyro_y = read_raw_data(GYRO_YOUT_H)
        gyro_z = read_raw_data(GYRO_ZOUT_H)
        
        #Full scale range +/- 250 degree/C as per sensitivity scale factor

        acc_y=0
        acc_z=0
        gyro_x=0
        gyro_y=0
        gyro_z=0

        Ax = acc_x/16384.0
        Ay = acc_y/16384.0
        Az = acc_z/16384.0
        
        Gx = gyro_x/131.0
        Gy = gyro_y/131.0
        Gz = gyro_z/131.0
        

        print ("Gx=%.2f" %Gx, u'\u00b0'+ "/s", "\tGy=%.2f" %Gy, u'\u00b0'+ "/s", "\tGz=%.2f" %Gz, u'\u00b0'+ "/s", "\tAx=%.2f g" %Ax, "\tAy=%.2f g" %Ay, "\tAz=%.2f g" %Az) 	
        sleep(1)
