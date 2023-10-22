import time
class Tmr:
  def __init__(self, seconds):
    self.seconds = seconds
    self.refTime = -1
    self.trigger = False
  
  def tmrStart(self):
    if self.refTime==-1:
      self.refTime = time.time()
    self.trigger = self.refTime + self.seconds < time.time()
    if self.trigger:
      self.refTime = -1
    else:
      pass
      
  def pulse(self):
    return self.trigger