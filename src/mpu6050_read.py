import smbus
from time import sleep
import traceback
from math import atan2, sqrt, pi

# MPU6050 Registers and their Address
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

bus = smbus.SMBus(1)  # or bus = smbus.SMBus(0) for older version boards
sleep(1)
bus.open(1)

def MPU_Init():
    # Wake up the MPU-6050
    bus.write_byte_data(DEVICE_ADDRESS, PWR_MGMT_1, 0)

    # Configure the accelerometer
    bus.write_byte_data(DEVICE_ADDRESS, 0x1C, 0x00)  # Set full scale range for the accelerometer to ±2g

    # Configure the gyroscope
    bus.write_byte_data(DEVICE_ADDRESS, 0x1B, 0x00)  # Set full scale range for the gyroscope to ±250°/s

    # Set clock source
    bus.write_byte_data(DEVICE_ADDRESS, PWR_MGMT_1, 0x01)  # Auto select best available clock source

    # Enable all sensors
    bus.write_byte_data(DEVICE_ADDRESS, PWR_MGMT_1, 0x00)

    # Set sample rate to 1kHz
    bus.write_byte_data(DEVICE_ADDRESS, SMPLRT_DIV, 0x07)

    print("MPU6050 initialized")

def read_raw_data(addr):
    try:
        high = bus.read_byte_data(DEVICE_ADDRESS, addr)
        sleep(0.001)  # Add a small delay between reads
        low = bus.read_byte_data(DEVICE_ADDRESS, addr+1)
        value = ((high << 8) | low)
        if value > 32768:
            value -= 65536
        return value
    except OSError as e:
        print(f"OSError in read_raw_data(0x{addr:02X}): {e}")
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"Unexpected error in read_raw_data(0x{addr:02X}): {e}")
        traceback.print_exc()
        return None

def read_block_data(addr, length):
    try:
        block = bus.read_i2c_block_data(DEVICE_ADDRESS, addr, length)
        return block
    except OSError as e:
        print(f"OSError in read_block_data(0x{addr:02X}, {length}): {e}")
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"Unexpected error in read_block_data(0x{addr:02X}, {length}): {e}")
        traceback.print_exc()
        return None

def calculate_roll_pitch(acc_x, acc_y, acc_z):
    roll = atan2(acc_y, acc_z) * 180 / pi
    pitch = atan2(-acc_x, sqrt(acc_y * acc_y + acc_z * acc_z)) * 180 / pi
    return roll, pitch

def main():
    MPU_Init()
    sleep(0.1)  # Short delay after initialization

    # Check WHO_AM_I register
    try:
        who_am_i = bus.read_byte_data(DEVICE_ADDRESS, WHO_AM_I)
        print(f"WHO_AM_I register value: 0x{who_am_i:02X}")
        if who_am_i != 0x68:
            print("Unexpected WHO_AM_I value. Check your connections and device address.")
    except OSError as e:
        print(f"Error reading WHO_AM_I register: {e}")

    print("\nTesting single register read (ACCEL_XOUT_H)...")
    for i in range(5):
        value = read_raw_data(ACCEL_XOUT_H)
        if value is not None:
            print(f"Read {i+1}: {value}")
        else:
            print(f"Read {i+1}: Failed")
        sleep(0.5)

    print("\nTesting multiple register read (ACCEL_XOUT_H to GYRO_ZOUT_L)...")
    for i in range(5):
        values = read_block_data(ACCEL_XOUT_H, 14)
        if values is not None:
            print(f"Read {i+1}: {values}")
        else:
            print(f"Read {i+1}: Failed")
        sleep(1)

    print("\nStarting continuous readings...")
    read_count = 0
    while True:
        try:
            read_count += 1
            print(f"\nRead #{read_count}")

            # Method 1: Individual reads
            acc_x = read_raw_data(ACCEL_XOUT_H)
            acc_y = read_raw_data(ACCEL_YOUT_H)
            acc_z = read_raw_data(ACCEL_ZOUT_H)
            gyro_x = read_raw_data(GYRO_XOUT_H)
            gyro_y = read_raw_data(GYRO_YOUT_H)
            gyro_z = read_raw_data(GYRO_ZOUT_H)

            if all(v is not None for v in [acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z]):
                print("Method 1 (Individual reads):")
                print(f"Acc: X={acc_x/16384:.2f}g, Y={acc_y/16384:.2f}g, Z={acc_z/16384:.2f}g")
                print(f"Gyro: X={gyro_x/131:.2f}°/s, Y={gyro_y/131:.2f}°/s, Z={gyro_z/131:.2f}°/s")
                roll, pitch = calculate_roll_pitch(acc_x, acc_y, acc_z)
                print(f"Roll: {roll:.2f}°, Pitch: {pitch:.2f}°")
            else:
                print("Method 1: Failed to read some values")

            # Method 2: Block read
            data = read_block_data(ACCEL_XOUT_H, 14)
            if data is not None:
                acc_x = (data[0] << 8) | data[1]
                acc_y = (data[2] << 8) | data[3]
                acc_z = (data[4] << 8) | data[5]
                temp = (data[6] << 8) | data[7]
                gyro_x = (data[8] << 8) | data[9]
                gyro_y = (data[10] << 8) | data[11]
                gyro_z = (data[12] << 8) | data[13]

                values = [acc_x, acc_y, acc_z, temp, gyro_x, gyro_y, gyro_z]
                for i in range(len(values)):
                    if values[i] > 32767:
                        values[i] -= 65536

                print("\nMethod 2 (Block read):")
                print(f"Acc: X={values[0]/16384:.2f}g, Y={values[1]/16384:.2f}g, Z={values[2]/16384:.2f}g")
                print(f"Temp: {values[3]/340 + 36.53:.2f}°C")
                print(f"Gyro: X={values[4]/131:.2f}°/s, Y={values[5]/131:.2f}°/s, Z={values[6]/131:.2f}°/s")
                roll, pitch = calculate_roll_pitch(values[0], values[1], values[2])
                print(f"Roll: {roll:.2f}°, Pitch: {pitch:.2f}°")
            else:
                print("Method 2: Failed to read block data")

        except Exception as e:
            print(f"Error in main loop: {e}")
            traceback.print_exc()

        sleep(1)

if __name__ == "__main__":
    main()