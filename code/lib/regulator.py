class PID:
    prdel = 0
    def __init__(self, feedbackTemp, P=0.2, I=0.0, D=0.0):
        self.kP = P
        self.kI = I
        self.kD = D
        self.intPart = 0
        self.intPartMax = 15
        self.period = 1
        self.setTemp = 0
        self.feedbackTemp = feedbackTemp

        self.lastError = 0
        self.pidValue = 0
        self.d = 0
    def getOnTime(self,setTemp):
        temp = self.feedbackTemp()
        self.setTemp = setTemp
        if type(temp) is not float:
            self.d = 0
        else:
            error = self.setTemp - temp
            self.intPart += error * self.period
            derPart = (error - self.lastError) / self.period
            self.lastError = error
            if self.intPart > self.intPartMax:
                self.intPart = self.intPartMax
            elif self.intPart < 0:
                self.intPart = 0
            self.pidValue = self.kP * error + (self.kI * self.intPart) + self.kD * derPart
            if self.pidValue > 40:
                self.d = 1
            elif self.pidValue < 0:
                self.d = 0
            else:
                self.d = self.pidValue / 40
            return self.period * self.d