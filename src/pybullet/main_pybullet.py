import sys
import os
import pybullet as p
import numpy as np
import time
import pybullet_data
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from pybullet_debuger import pybulletDebug  
from kinematic_model import robotKinematics
from gaitPlanner import trotGait
from servo_config import motor_config


physicsClient = p.connect(p.DIRECT)#or p.DIRECT for non-graphical version
p.setAdditionalSearchPath(pybullet_data.getDataPath()) #optionally
p.setGravity(0,0,-9.8)

fr_angles_list = []
fl_angles_list = []
br_angles_list = []
bl_angles_list = []

cubeStartPos = [0,0,0.2]
FixedBase = False #if fixed no plane is imported
urdf_path = os.path.join(os.path.dirname(__file__), '../4leggedRobot_with_sensors.urdf')

if (FixedBase == False):
    p.loadURDF("plane.urdf")
boxId = p.loadURDF(urdf_path,cubeStartPos, useFixedBase=FixedBase)

jointIds = []
paramIds = [] 
time.sleep(0.5)
servo = motor_config()
servo.relax_all_motors()
for j in range(p.getNumJoints(boxId)):
#    p.changeDynamics(boxId, j, linearDamping=0, angularDamping=0)
    info = p.getJointInfo(boxId, j)
    print(info)
    jointName = info[1]
    jointType = info[2]
    jointIds.append(j)
    
footFR_index = 3
footFL_index = 7
footBR_index = 11
footBL_index = 15   

pybulletDebug = pybulletDebug()
robotKinematics = robotKinematics()
trot = trotGait() 

#robot properties
"""initial foot position"""
#foot separation (Ydist = 0.16 -> tetta=0) and distance to floor
Xdist = 0.20
Ydist = 0.15
height = 0.15
#body frame to foot frame vector
bodytoFeet0 = np.matrix([[ Xdist/2 , -Ydist/2 , -height],
                         [ Xdist/2 ,  Ydist/2 , -height],
                         [-Xdist/2 , -Ydist/2 , -height],
                         [-Xdist/2 ,  Ydist/2 , -height]])

T = 0.5 #period of time (in seconds) of every step
offset = np.array([0.5 , 0. , 0. , 0.5]) #defines the offset between each foot step in this order (FR,FL,BR,BL)

p.setRealTimeSimulation(1)
    
while(True):
    lastTime = time.time()
    pos , orn , L , angle , Lrot , T = pybulletDebug.cam_and_robotstates(boxId)  
    #calculates the feet coord for gait, defining length of the step and direction (0º -> forward; 180º -> backward)
    bodytoFeet = trot.loop(L , angle , Lrot , T , offset , bodytoFeet0)

#####################################################################################
#####   kinematics Model: Input body orientation, deviation and foot position    ####
#####   and get the angles, neccesary to reach that position, for every joint    ####
    FR_angles, FL_angles, BR_angles, BL_angles , transformedBodytoFeet = robotKinematics.solve(orn , pos , bodytoFeet)
    #print("FR:", FR_angles, "FL:", FL_angles, "BR:", BR_angles, "BL:", BL_angles)
    #move movable joints
    for i in range(0, footFR_index):
        p.setJointMotorControl2(boxId, i, p.POSITION_CONTROL, FR_angles[i - footFR_index])
    for i in range(footFR_index + 1, footFL_index):
        p.setJointMotorControl2(boxId, i, p.POSITION_CONTROL, FL_angles[i - footFL_index])
    for i in range(footFL_index + 1, footBR_index):
        p.setJointMotorControl2(boxId, i, p.POSITION_CONTROL, BR_angles[i - footBR_index])
    for i in range(footBR_index + 1, footBL_index):
        p.setJointMotorControl2(boxId, i, p.POSITION_CONTROL, BL_angles[i - footBL_index])
    
    servo.moveAbsAngle(servo.back_left_hip, 180)
    servo.moveAbsAngle(servo.back_left_upper, np.rad2deg(BL_angles[2]))
    servo.moveAbsAngle(servo.back_left_lower, np.rad2deg(BL_angles[3]))
    
    time.sleep(0.01)

#    print(time.time() - lastTime)
p.disconnect()
