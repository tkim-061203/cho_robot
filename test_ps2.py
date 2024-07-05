import spidev
import time

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Open bus 0, device (CS) 0
spi.max_speed_hz = 5000

# PS2 controller initialization sequence
def init_ps2():
    commands = [
        [0x01, 0x43, 0x00, 0x01, 0x00],
        [0x01, 0x44, 0x00, 0x01, 0x03, 0x00, 0x00, 0x00, 0x00],
        [0x01, 0x43, 0x00, 0x01, 0x00],
        [0x01, 0x4D, 0x00, 0x00, 0x00],
        [0x01, 0x4C, 0x00, 0x00, 0x00]
    ]
    for command in commands:
        spi.xfer2(command)
        time.sleep(0.1)

# Function to read PS2 controller data
def read_ps2():
    command = [0x01, 0x42, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    response = spi.xfer2(command)
    return response

# Function to interpret PS2 controller data
def interpret_data(data):
    button_mask = {
        'Select': 0x01, 'L3': 0x02, 'R3': 0x04, 'Start': 0x08,
        'Up': 0x10, 'Right': 0x20, 'Down': 0x40, 'Left': 0x80,
        'L2': 0x01, 'R2': 0x02, 'L1': 0x04, 'R1': 0x08,
        'Triangle': 0x10, 'Circle': 0x20, 'Cross': 0x40, 'Square': 0x80
    }

    buttons = {
        'Select': False, 'L3': False, 'R3': False, 'Start': False,
        'Up': False, 'Right': False, 'Down': False, 'Left': False,
        'L2': False, 'R2': False, 'L1': False, 'R1': False,
        'Triangle': False, 'Circle': False, 'Cross': False, 'Square': False
    }

    # The data format for the buttons is in data[3] and data[4]
    for button, mask in button_mask.items():
        if button in ['Select', 'L3', 'R3', 'Start', 'Up', 'Right', 'Down', 'Left']:
            buttons[button] = not (data[3] & mask)
        else:
            buttons[button] = not (data[4] & mask)

    return buttons

# Initialize PS2 controller
init_ps2()

# Main loop to read and display button presses
while True:
    data = read_ps2()
    buttons = interpret_data(data)
    pressed_buttons = [button for button, pressed in buttons.items() if pressed]
    if pressed_buttons:
        print(f'Buttons pressed: {pressed_buttons}')
    time.sleep(0.1)
