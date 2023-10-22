class PID:
  def __init__(self, Ts, Tf):
    self.Ts = Ts
    self.Tf = Tf
    self.yf_prev = 20
    self.AlmActive = False
    self.PV = 0
    self.e_k1 = 0
    self.u_i_k = 0
    
  def __LowPassFilter(self, y):
    a = self.Ts/(self.Tf+self.Ts);
    yf = (1-a)*self.yf_prev + a*y
    self.yf_prev = yf
    return yf;
    
  def __trunc(self,floatNum, decimal_places):
    multiplier = 10 ** decimal_places
    return int(floatNum * multiplier) / multiplier 
    
  def config(self, AlmLimit, Tf, Ts):
    self.Tf = Tf
    self.Ts = Ts
    if self.PV > AlmLimit:
      self.AlmActive = True
    
  def PV(self):
    return float(self.PV)

  def almActive(self):
    return self.AlmActive
      
  def ackAlm(self):
    self.AlmActive = False
      
  def clip(self,u, uMax, uMin):
    if u > uMax:
      u = uMax
    if u < uMin:
      u = uMin
    if u <= uMax and u >= uMin:
      u = u
    return u
    
  def PID(self, y_k,sp ,directAction, kp,Ti, Td, uMax, uMin):
    PV = self.__LowPassFilter(y_k)
    self.PV = self.__trunc(PV, 2)

    Gain = kp
    if directAction:
      Gain = -1*kp
    e_k = sp - self.PV        # Error
    u_p_k = Gain * e_k   	# P-Term
    u_d_k = Gain * Td * (e_k - self.e_k1) / self.Ts # D-Term
    self.e_k1 = e_k 							# Last Error
    self.u_i_k += (Gain * e_k * self.Ts) / Ti       # I-Term
    self.u_i_k = self.clip(self.u_i_k,uMax, uMin)   # Anti windup of I-term
    
    return self.clip(u_p_k + self.u_i_k + u_d_k, uMax, uMin)
    
  
      
