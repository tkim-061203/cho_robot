import time
import board
import busio
from adafruit_pca9685 import PCA9685

# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)

# Set frequency to exactly 50Hz
pca.frequency = 50

# Calculate pulse values for standard servo timing
# For 50Hz, full period is 20ms (0xFFFF counts)
# 1ms = 0.05 * 0xFFFF = 0x1333
# 1.5ms = 0.075 * 0xFFFF = 0x1998
# 2ms = 0.1 * 0xFFFF = 0x1FFF

try:
    while True:
        print("0 degrees (1ms pulse)")
        pca.channels[0].duty_cycle = 0x1333
        time.sleep(2)
        
        print("90 degrees (1.5ms pulse)")
        pca.channels[0].duty_cycle = 0x1998
        time.sleep(2)
        
        print("180 degrees (2ms pulse)")
        pca.channels[0].duty_cycle = 0x1FFF
        time.sleep(2)

except KeyboardInterrupt:
    pca.deinit()