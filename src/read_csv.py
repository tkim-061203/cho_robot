import pandas as pd

# Define the file path
file_path = 'C:/Users/KIM/Desktop/pi/telemetry/robot_angle.csv'

# Read the CSV file
df = pd.read_csv(file_path)

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

# Print the arrays to verify
FR_1_array, FR_2_array, FR_3_array, FL_1_array, FL_2_array, FL_3_array, BR_1_array, BR_2_array, BR_3_array, BL_1_array, BL_2_array, BL_3_array

print(FL_1_array, FL_2_array, FL_3_array, BL_1_array, BL_2_array, BL_3_array)

