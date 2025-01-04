import numpy as np
from simple_pid import PID

class stabilize:
    def __init__(self):        
        """
        Initialize PID controllers for x, y, roll and pitch.
        Also, define the initial CoM position and the parameters for the compliant control.
        """
        self.CoM = np.array([-0.01 , 0. , 0.01])
        
        self.pidX = PID(-0.0005 , 0. , 0.00001 , setpoint=0.)
        self.pidY = PID( 0.00025 , 0. , 0.00001 , setpoint=0.)
        self.pidRoll =  PID(-0.005 , 0. , 0.0001 , setpoint=0.)
        self.pidPitch = PID(-0.005 , 0. , 0.0001 , setpoint=0.)
        self.pidX.sample_time = 0.025
        self.pidY.sample_time = 0.025
        self.pidRoll.sample_time = 0.025 
        self.pidPitch.sample_time = 0.025 
        self.pidX.output_limits = (-0.03, 0.03) 
        self.pidY.output_limits = (-0.03, 0.03) 
        self.pidRoll.output_limits = (-np.pi/4, np.pi/4) 
        self.pidPitch.output_limits = (-np.pi/4, np.pi/4) 
        
        self.collision = False
        self.forceAngle = 0.
        self.Lcomplianti = 0.
        self.Lcompliant = []
        self.i = 0
    def centerPoint(self , actualPitch , actualRoll):
                    
        Upid_xorn = self.pidRoll(actualRoll)
        Upid_yorn = self.pidPitch(actualPitch)
        Upid_x = self.pidX(actualPitch)
        Upid_y = self.pidY(actualRoll)
        
        return Upid_x , Upid_y , Upid_xorn , Upid_yorn
    
    
    def bodyCompliant(self , Xacc , Yacc , compliantMode):
        """
        This function is used for body compliant control. If the compliant mode is activated, and the acceleration in x or y 
        irection is higher than 7000, then a collision is detected and the robot starts to move compliantly. 
        The force angle is calculated and the compliant length is calculated from the force module. 
        The compliant length is then decreased linearly until it is zero. 
        The function returns the force module, the force angle, 
        the compliant length and a boolean indicating if the robot is in collision or not.
        
        Parameters:
        Xacc (float): acceleration in x direction
        Yacc (float): acceleration in y direction
        compliantMode (bool): boolean indicating if the compliant mode is activated
        
        Returns:
        forceModule (float): force module
        forceAngle (float): force angle in degrees
        Lcompliant (float): compliant length
        collision (bool): boolean indicating if the robot is in collision or not
        """
        if compliantMode == True:
            if Xacc >= 7000 or Yacc >= 7000:
               self.collision = True
               self.forceAngle = np.rad2deg(np.arctan2(Yacc, Xacc))
               forceModulei = np.sqrt(Xacc**2 + Yacc**2)
               self.Lcomplianti = forceModulei/1000
               if self.Lcomplianti >= 0.6:
                   self.Lcomplianti  = .6
               self.Lcompliant = np.linspace(self.Lcomplianti,0.,100)
    
            if self.collision == True:
                self.Lcomplianti = self.Lcompliant[self.i]
                if self.Lcomplianti >= 0.6:
                   self.Lcomplianti  = .6
                self.forceAngle = self.forceAngle  
                self.i += 1
                if self.Lcompliant[self.i] <= 0.:
                    self.collision = False
                    self.i=0
                    self.forceAngle = 0.
            forceModulei = np.sqrt(Xacc**2 + Yacc**2)
        else:
            forceModulei = np.rad2deg(np.arctan2(Yacc, Xacc))
            self.forceAngle = 0.
            self.Lcomplianti = 0.
            self.i=0
        
        return forceModulei , self.forceAngle , self.Lcomplianti , self.collision
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    