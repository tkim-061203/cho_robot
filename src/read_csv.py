import pandas as pd
import time
from servo_config import motor_config

# Define the file path
file_path = '../telemetry/robot_angle.csv'

# Read the CSV file
df = pd.read_csv(file_path)
df = df.round()

# Display the content of the DataFrame
df.head()  # Show the first few rows of the DataFrame

# Convert each column to a numpy array
FR_1_array = df['FR_1'].to_numpy()
FR_2_array = df['FR_2'].to_numpy()
FR_3_array = df['FR_3'].to_numpy()
FL_1_array = df['FL_1'].to_numpy()
FL_2_array = df['FL_2'].to_numpy()
FL_3_array = df['FL_3'].to_numpy()
BR_1_array = df['BR_1'].to_numpy()
BR_2_array = df['BR_2'].to_numpy()
BR_3_array = df['BR_3'].to_numpy()
BL_1_array = df['BL_1'].to_numpy()
BL_2_array = df['BL_2'].to_numpy()
BL_3_array = df['BL_3'].to_numpy()

servo = motor_config()

servo.relax_all_motors()
servo.moveAbsAngle(servo.back_left_hip, 0)

for i in range(len(BL_1_array)):
    print(BL_1_array[i],BL_2_array[i],BL_3_array[i])
    servo.moveAbsAngle(servo.back_left_hip, 90)
    servo.moveAbsAngle(servo.back_left_upper, BL_2_array[i])
    servo.moveAbsAngle(servo.back_left_lower, BL_3_array[i])
    
    time.sleep(0.25)
# servo.moveAbsAngle(servo.front_left_hip, FL_1_array[0])
# servo.moveAbsAngle(servo.back_left_upper, 100)
# servo.moveAbsAngle(servo.back_left_lower, 180)
