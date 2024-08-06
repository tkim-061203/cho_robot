import numpy as np
from pyPS4Controller.controller import Controller
import threading
import time

class Joystick(Controller):
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        self.L3 = np.array([0., 0.])
        self.R3 = np.array([0., 0.])
        
        self.T = 0.4
        self.V = 0.
        self.angle = 0.
        self.Wrot = 0.
        self.compliantMode = False
        self.poseMode = False
        self.CoM_pos = np.zeros(3)
        self.CoM_orn = np.zeros(3)
        self.calibration = 0
        
        self.running = True
        self.display_thread = threading.Thread(target=self.continuous_display)
        self.display_thread.start()

    def on_L3_up(self, value):
        self.L3[1] = -value / 32767.0
        self.update_values()

    def on_L3_down(self, value):
        self.L3[1] = value / 32767.0
        self.update_values()

    def on_L3_left(self, value):
        self.L3[0] = -value / 32767.0
        self.update_values()

    def on_L3_right(self, value):
        self.L3[0] = value / 32767.0
        self.update_values()

    def on_R3_up(self, value):
        self.R3[1] = -value / 32767.0
        self.update_values()

    def on_R3_down(self, value):
        self.R3[1] = value / 32767.0
        self.update_values()

    def on_R3_left(self, value):
        self.R3[0] = -value / 32767.0
        self.update_values()

    def on_R3_right(self, value):
        self.R3[0] = value / 32767.0
        self.update_values()

    def on_up_arrow_press(self):
        self.CoM_pos[2] += 0.002
        self.update_values()

    def on_down_arrow_press(self):
        self.CoM_pos[2] -= 0.002
        self.update_values()

    def on_right_arrow_press(self):
        self.T += 0.05
        self.update_values()

    def on_left_arrow_press(self):
        self.T -= 0.05
        self.update_values()

    def on_square_press(self):
        self.compliantMode = not self.compliantMode
        self.update_values()

    def on_triangle_press(self):
        self.poseMode = not self.poseMode
        self.update_values()

    def update_values(self):
        if not self.poseMode:           
            self.V = np.sqrt(self.L3[1]**2 + self.L3[0]**2)
            self.angle = np.rad2deg(np.arctan2(-self.L3[0], -self.L3[1]))
            self.Wrot = -self.R3[0]
            if self.V <= 0.035:
                self.V = 0.
            if abs(self.Wrot) <= 0.035:
                self.Wrot = 0.
        else:
            self.CoM_orn[0] = np.deg2rad(self.R3[0] * 30)
            self.CoM_orn[1] = np.deg2rad(self.L3[1] * 30)
            self.CoM_orn[2] = -np.deg2rad(self.L3[0] * 30)
            self.CoM_pos[0] = -self.R3[1] / 5

    def show(self):
        print("\033[H\033[J", end="")  # Clear the console
        print("Joystick State:")
        print(f"CoM Position: {self.CoM_pos}")
        print(f"CoM Orientation: {self.CoM_orn}")
        print(f"Velocity: {self.V}")
        print(f"Angle: {-self.angle}")
        print(f"Angular Velocity: {-self.Wrot}")
        print(f"T: {self.T}")
        print(f"Compliant Mode: {self.compliantMode}")
        print(f"L3: {self.L3}")
        print(f"R3: {self.R3}")

    def continuous_display(self):
        while self.running:
            self.show()
            time.sleep(0.1)  # Update every 0.1 seconds

    def listen(self, timeout=30):
        try:
            Controller.listen(self, timeout=timeout)
        finally:
            self.running = False
            self.display_thread.join()

if __name__ == "__main__":
    ps4 = Joystick(interface="/dev/input/js0", connecting_using_ds4drv=False)
    ps4.listen()