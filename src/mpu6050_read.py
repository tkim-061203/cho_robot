import smbus
import time
from math import atan2, sqrt, pi

class MPU6050:
    MPU6050_ADDR = 0x68
    PWR_MGMT_1 = 0x6B
    ACCEL_XOUT_H = 0x3B
    ACCEL_YOUT_H = 0x3D
    ACCEL_ZOUT_H = 0x3F

    def __init__(self, bus_number=1):
        self.bus = smbus.SMBus(bus_number)
        self.init_mpu6050()

    def init_mpu6050(self):
        self.bus.write_byte_data(self.MPU6050_ADDR, self.PWR_MGMT_1, 0)

    def read_word_2c(self, addr):
        high = self.bus.read_byte_data(self.MPU6050_ADDR, addr)
        low = self.bus.read_byte_data(self.MPU6050_ADDR, addr + 1)
        val = (high << 8) + low
        if val >= 0x8000:
            return -((65535 - val) + 1)
        else:
            return val

    def get_accel_data(self):
        acc_x = self.read_word_2c(self.ACCEL_XOUT_H)
        acc_y = self.read_word_2c(self.ACCEL_YOUT_H)
        acc_z = self.read_word_2c(self.ACCEL_ZOUT_H)
        return acc_x, acc_y, acc_z

    def calculate_roll_pitch(self, acc_x, acc_y, acc_z):
        roll = atan2(acc_y, acc_z) * 180 / pi
        pitch = atan2(-acc_x, sqrt(acc_y * acc_y + acc_z * acc_z)) * 180 / pi
        return roll, pitch

    def run(self, delay=0.5):
        while True:
            acc_x, acc_y, acc_z = self.get_accel_data()
            roll, pitch = self.calculate_roll_pitch(acc_x, acc_y, acc_z)
            print(f"Xacc: {acc_x}, Yacc: {acc_y}, realRoll: {roll:.2f}, realPitch: {pitch:.2f}")
            time.sleep(delay)

if __name__ == "__main__":
    mpu = MPU6050()
    mpu.run()