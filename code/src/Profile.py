class Profile:

    def __init__(self, readTemp, profile: str):
        # leadedProfile = [(125,120),(50,60),(25,25),(0,10)] #(delta temp,delta seconds), start at 25
        # leadedProfile = [(125,120),(50,60),(25,25),(0,10)] #(delta temp,delta seconds), start at 25
        #leadedProfile = [(150, 120), (200, 180), (225, 205), (225, 215)]  # (temp,seconds), start at 25
        leadedProfile = [(100, 30), (150, 120), (183, 150), (238, 210)] # (temp,seconds), start at 25
        leadFreeProfile = [(150, 90), (175, 180), (217, 210), (253, 240)] # (temp,seconds), start at 25

        self.readTemp = readTemp
        self.slope = 0
        self.tempOffset = 0
        if profile == "leaded":
            self.profile = leadedProfile
        if profile == "leadfree":
            self.profile = leadFreeProfile
        self.actualPoint = self.profile[0]
        self.linearize(0, self.actualPoint, (self.readTemp(), 0))
        self.changeTime = 0


    def readProfile(self):
        return self.profile
    def linearize(self, time, point, lastPoint):
        #actualTemp = self.readTemp()
        tempDelta = point[0] - lastPoint[0]
        timeDelta = point[1] - lastPoint[1]
        self.slope = (tempDelta / timeDelta)
        self.tempOffset = lastPoint[0]


    def calculateTempForTime(self, time) -> float:
        if time < self.actualPoint[1]:
            return self.slope * (time - self.changeTime) + self.tempOffset
        else:
            newIndex = self.profile.index(self.actualPoint)+1
            if newIndex > len(self.profile)-1:
                return 0
            else:
                self.changeTime = time
                self.actualPoint = self.profile[newIndex]
                self.linearize(time, self.actualPoint, self.profile[newIndex-1])
                return self.slope * (time - self.changeTime) + self.tempOffset