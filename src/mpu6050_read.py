import smbus
from time import sleep
import traceback
from math import atan2, sqrt, pi

class MPU6050:
    DEVICE_ADDRESS = 0x68
    PWR_MGMT_1 = 0x6B
    SMPLRT_DIV = 0x19
    CONFIG = 0x1A
    GYRO_CONFIG = 0x1B
    INT_ENABLE = 0x38
    ACCEL_XOUT_H = 0x3B
    ACCEL_YOUT_H = 0x3D
    ACCEL_ZOUT_H = 0x3F
    GYRO_XOUT_H = 0x43
    GYRO_YOUT_H = 0x45
    GYRO_ZOUT_H = 0x47
    WHO_AM_I = 0x75

    def __init__(self, bus_id=1):
        self.bus = smbus.SMBus(bus_id)
        sleep(1)
        self.bus.open(bus_id)
        self.init_sensor()

    def init_sensor(self):
        self.bus.write_byte_data(self.DEVICE_ADDRESS, self.PWR_MGMT_1, 0)
        self.bus.write_byte_data(self.DEVICE_ADDRESS, 0x1C, 0x00)  # Accelerometer range ±2g
        self.bus.write_byte_data(self.DEVICE_ADDRESS, self.GYRO_CONFIG, 0x00)  # Gyro range ±250°/s
        self.bus.write_byte_data(self.DEVICE_ADDRESS, self.PWR_MGMT_1, 0x01)
        self.bus.write_byte_data(self.DEVICE_ADDRESS, self.SMPLRT_DIV, 0x07)
        print("MPU6050 initialized")

    def read_raw_data(self, addr):
        try:
            high = self.bus.read_byte_data(self.DEVICE_ADDRESS, addr)
            sleep(0.001)
            low = self.bus.read_byte_data(self.DEVICE_ADDRESS, addr + 1)
            value = (high << 8) | low
            if value > 32768:
                value -= 65536
            return value
        except Exception as e:
            print(f"Error reading data from 0x{addr:02X}: {e}")
            traceback.print_exc()
            return None

    def get_accel_data(self):
        return (
            self.read_raw_data(self.ACCEL_XOUT_H),
            self.read_raw_data(self.ACCEL_YOUT_H),
            self.read_raw_data(self.ACCEL_ZOUT_H)
        )

    def get_gyro_data(self):
        return (
            self.read_raw_data(self.GYRO_XOUT_H),
            self.read_raw_data(self.GYRO_YOUT_H),
            self.read_raw_data(self.GYRO_ZOUT_H)
        )

    def calculate_roll_pitch(self, acc_x, acc_y, acc_z):
        roll = atan2(acc_y, acc_z) * 180 / pi
        pitch = atan2(-acc_x, sqrt(acc_y**2 + acc_z**2)) * 180 / pi
        return roll, pitch

    def get_sensor_data(self):
        acc_x, acc_y, acc_z = self.get_accel_data()
        gyro_x, gyro_y, gyro_z = self.get_gyro_data()
        roll, pitch = self.calculate_roll_pitch(acc_x, acc_y, acc_z)
        return {
            "acceleration": {"x": acc_x / 16384, "y": acc_y / 16384, "z": acc_z / 16384},
            "gyroscope": {"x": gyro_x / 131, "y": gyro_y / 131, "z": gyro_z / 131},
            "roll": roll,
            "pitch": pitch
        }

if __name__ == "__main__":
    mpu = MPU6050Reader()
    while True:
        data = mpu.get_sensor_data()
        print(data)
        sleep(1)
