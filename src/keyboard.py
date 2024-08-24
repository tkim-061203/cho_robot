import numpy as np
import threading
import time
from pynput import keyboard

class KeyboardController:
    def __init__(self):
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

        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def on_press(self, key):
        try:
            if key.char == 'w':
                self.L3[1] = -1
            elif key.char == 's':
                self.L3[1] = 1
            elif key.char == 'a':
                self.L3[0] = -1
            elif key.char == 'd':
                self.L3[0] = 1
            elif key.char == 'i':
                self.R3[1] = -1
            elif key.char == 'k':
                self.R3[1] = 1
            elif key.char == 'j':
                self.R3[0] = -1
            elif key.char == 'l':
                self.R3[0] = 1
        except AttributeError:
            if key == keyboard.Key.up:
                self.CoM_pos[2] += 0.002
            elif key == keyboard.Key.down:
                self.CoM_pos[2] -= 0.002
            elif key == keyboard.Key.right:
                self.T += 0.05
            elif key == keyboard.Key.left:
                self.T -= 0.05
            elif key == keyboard.Key.space:
                self.compliantMode = not self.compliantMode
            elif key == keyboard.Key.enter:
                self.poseMode = not self.poseMode
        
        self.update_values()

    def on_release(self, key):
        try:
            if key.char in ['w', 's']:
                self.L3[1] = 0
            elif key.char in ['a', 'd']:
                self.L3[0] = 0
            elif key.char in ['i', 'k']:
                self.R3[1] = 0
            elif key.char in ['j', 'l']:
                self.R3[0] = 0
        except AttributeError:
            pass
        
        self.update_values()
        
        if key == keyboard.Key.esc:
            self.running = False
            return False

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
        print("Keyboard Controller State:")
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

    def listen(self):
        try:
            self.listener.join()
        finally:
            self.running = False
            self.display_thread.join()
    def get_command_values(self):
        """
        Returns:
            tuple: (commandPose, commandOrn, V, angle, Wrot, T, compliantMode)
        """
        commandPose = self.CoM_pos
        commandOrn = self.CoM_orn
        V = self.V
        angle = -self.angle 
        Wrot = -self.Wrot
        T = self.T
        compliantMode = self.compliantMode

        return commandPose, commandOrn, V, angle, Wrot, T, compliantMode

if __name__ == "__main__":
    controller = KeyboardController()
    controller.listen()