import numpy as np
import time
import csv
 
from kinematic_model import robotKinematics
from joystick import Joystick
from gaitPlanner import trotGait
from CoM_stabilization import stabilize
from mpu6050_read import MPU6050
from servo_config import motor_config


##This part of code is just to save the raw telemetry data.
fieldnames = ["t","roll","pitch"]
with open('/home/kim/cho_robot/telemetry/data_t.csv','w') as csv_file:
    csv_writer = csv.DictWriter(csv_file,fieldnames = fieldnames)
    csv_writer.writeheader()

# def update_data():
#     with open('/home/kim/cho_robot/telemetry/data_t.csv','a') as csv_file:
#         csv_writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
#         info = {"t" :  t,
#                 "roll" : realRoll,
#                 "pitch" : realPitch}
#         csv_writer.writerow(info)


robotKinematics = robotKinematics()
joystick =  Joystick('/dev/input/event5')
trot = trotGait() 
control = stabilize()
mpu = MPU6050()
servo= motor_config()

servo.relax_all_motors()
time.sleep(2)
#robot properties
"""initial safe position"""
#angles
targetAngs = np.array([0 , np.pi/4 , -np.pi/2, 0 ,#BR
                        0 , np.pi/4 , -np.pi/2, 0 ,#BL
                        0 , np.pi/4 , -np.pi/2, 0 ,#FL
                        0 , np.pi/4 , -np.pi/2, 0 ])#FR

#FR_0  to FR_4 
#FRcoord = np.matrix([0. , -3.6 , -0.15])
#FLcoord = np.matrix([0. ,  3.6 , -0.15])
#BRcoord = np.matrix([0. , -3.6 , -0.15])
#BLcoord = np.matrix([0. ,  3.6 , -0.15])

"initial foot position"
#foot separation (0.182 -> tetta=0) and distance to floor
Ydist = 0.18
Xdist = 0.25
height = 0.16
#body frame to foot frame vector (0.08/-0.11 , -0.07 , -height)
bodytoFeet0 = np.matrix([[ 0.085 , -0.075 , -height],
                         [ 0.085 ,  0.075 , -height],
                         [-0.11 , -0.075 , -height],
                         [-0.11 ,  0.075 , -height]])

orn = np.array([0. , 0. , 0.])
pos = np.array([0. , 0. , 0.])
Upid_yorn = [0.]
Upid_y = [0.]
Upid_xorn = [0.]
Upid_x = [0.]
startTime = time.time()
lastTime = startTime
t = []
       
        
T = 0.4 #period of time (in seconds) of every step
offset = np.array([0. , 0.5 , 0.5 , 0.]) #defines the offset between each foot step in this order (FR,FL,BR,BL)
                                         # [0. , 0.25 , 0.75 , 0.5] creep gait
interval = 0.030
print("Finish setup")

def run_servo(FR_angles, FL_angles, BR_angles, BL_angles):
    servo.moveAbsAngle(servo.front_left_hip, np.rad2deg(FL_angles[0]))
    servo.moveAbsAngle(servo.front_left_upper, np.rad2deg(FL_angles[1]))
    servo.moveAbsAngle(servo.front_left_lower, np.rad2deg(FL_angles[2]))
    servo.moveAbsAngle(servo.front_right_hip, np.rad2deg(FR_angles[0]))
    servo.moveAbsAngle(servo.front_right_upper, np.rad2deg(FR_angles[1]))
    servo.moveAbsAngle(servo.front_right_lower, np.rad2deg(FR_angles[2]))
    servo.moveAbsAngle(servo.back_right_hip, np.rad2deg(BR_angles[0]))
    servo.moveAbsAngle(servo.back_right_upper, np.rad2deg(BR_angles[1]))
    servo.moveAbsAngle(servo.back_right_lower, np.rad2deg(BR_angles[2]))
    servo.moveAbsAngle(servo.back_left_hip, np.rad2deg(BL_angles[0]))
    servo.moveAbsAngle(servo.back_left_upper, np.rad2deg(BL_angles[1]))
    servo.moveAbsAngle(servo.back_left_lower, np.rad2deg(BL_angles[2]))


for k in range(100000000000):
    if (time.time()-lastTime >= interval):
        loopTime = time.time() - lastTime
        lastTime = time.time()
        t = time.time() - startTime
        
        commandPose , commandOrn , V , angle , Wrot , T , compliantMode =   joystick.read()
        
        Xacc , Yacc , Zacc = mpu.get_accel_data()
        realRoll , realPitch = mpu.get_roll_pitch()

        forceModule , forceAngle , Vcompliant , collision = control.bodyCompliant(Xacc , Yacc , compliantMode)
        #calculates the feet coord for gait, defining length of the step and direction (0º -> forward; 180º -> backward)
        if joystick.poseMode:
            print("In pose mode")
            bodytoFeet = bodytoFeet0
        else:
            print("Out pose mode")
            bodytoFeet  = trot.loop(V + Vcompliant , angle + forceAngle , Wrot , T , offset , bodytoFeet0)
        
        #####################################################################################
        #####   kinematics Model: Input body orientation, deviation and foot position    ####
        #####   and get the angles, neccesary to reach that position, for every joint    ####
        FR_angles, FL_angles, BR_angles, BL_angles , transformedBodytoFeet, __ = robotKinematics.solve(orn + commandOrn, pos + commandPose , bodytoFeet)

        # print (loopTime, realRoll , realPitch)
        run_servo(FR_angles, FL_angles, BR_angles, BL_angles)
        time.sleep(0.2)
        # update_data()
