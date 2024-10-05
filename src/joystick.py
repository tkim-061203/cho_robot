#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from evdev import InputDevice, categorize, ecodes
from select import select
import numpy as np
import time 

class Joystick:
    def __init__(self , event):
        #python3 /usr/local/lib/python3.8/dist-packages/evdev/evtest.py for identify event
        self.gamepad = InputDevice(event)
        self.L3 = np.array([0. , 0.])
        self.R3 = np.array([0. , 0.])
        
        self.x=0
        self.triangle=0
        self.circle=0
        self.square=0
        
        self.T = 0.4
        self.compliantMode = False
        self.CoM_move = np.zeros(3)

        self.yaw = 0.0  # Initialize yaw
        self.pitch = 0.0  # Initialize pitch
        
    def read(self):
        r, w, x = select([self.gamepad.fd], [], [], 0.)
        
        if r:
            for event in self.gamepad.read():
                if event.type == ecodes.EV_KEY:
                    if event.code == 308:  # Square button
                        if event.value == 1:
                            self.compliantMode = not self.compliantMode
                    elif event.code == 310:  # R1 button
                        if event.value == 1:
                            self.CoM_move[0] += 0.0005
                    elif event.code == 311:  # L1 button
                        if event.value == 1:
                            self.CoM_move[0] -= 0.0005
                
                elif event.type == ecodes.EV_ABS:
                    if event.code == 17:  # D-pad up/down
                        self.dpad_y = event.value
                        if event.value == -1:  # Up arrow
                            self.T += 0.05
                        elif event.value == 1:  # Down arrow
                            self.T -= 0.05
                    elif event.code == 0:  # Left stick X-axis
                        self.L3[0] = event.value - 127
                    elif event.code == 1:  # Left stick Y-axis
                        self.L3[1] = event.value - 127
                    elif event.code == 3:  # Right stick X-axis
                        self.R3[0] = event.value - 127
                        self.yaw = np.deg2rad(self.R3[0] / 3)
                    elif event.code == 4:  # Right stick Y-axis
                        self.R3[1] = event.value - 127
                        self.pitch = np.deg2rad(self.R3[1] / 2)

        L = np.sqrt(self.L3[1]**2 + self.L3[0]**2) / 250.
        angle = np.rad2deg(np.arctan2(-self.L3[0], -self.L3[1]))
        Wrot = -self.R3[0] / 250.

        if L <= 0.035:
            L = 0.
        if -0.035 <= Wrot <= 0.035:
            Wrot = 0.

        return self.CoM_move, L, -angle, -Wrot, self.T, self.compliantMode, self.yaw, self.pitch

# if __name__ == "__main__":
#     joy = Joystick('/dev/input/event5')  # Replace with your event file

# while True:
#     # Read joystick input
#     CoM_move, L, angle, Lrot, T, compliantMode, yaw, pitch = joy.read()

#     # Print the values
#     print(f"CoM_move: {CoM_move}, L: {L}, angle: {angle}, Lrot: {Lrot}")
#     print(f"T: {T}, compliantMode: {compliantMode}, yaw: {yaw}, pitch: {pitch}")

#     # Add a small delay to avoid excessive CPU usage
#     time.sleep(0.01)