import spidev
import time

# Create SPI object
spi = spidev.SpiDev()
spi.open(0, 0)  # Open bus 0, device 0 (CE0)

# Set SPI speed and mode
spi.max_speed_hz = 50000
spi.mode = 0

def read_spi(channel):
    # Read data from the specified channel (0 or 1)
    # Adjust the command based on your device's protocol
    cmd = [0b01101000 | ((channel & 0x07) << 4), 0x00]
    response = spi.xfer2(cmd)
    # Convert the response to a 10-bit value
    result = ((response[0] & 0x03) << 8) + response[1]
    return result

try:
    while True:
        # Read data from channel 0
        value = read_spi(0)
        print(f"SPI Read Value: {value}")
        time.sleep(1)
except KeyboardInterrupt:
    spi.close()
