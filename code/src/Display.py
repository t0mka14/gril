import gc
import uasyncio

from lib.pico_i2c_lcd import I2cLcd
from lib.regulator import PID
from src.Profile import Profile


class Display:
    def __init__(self, lcd: I2cLcd, setTemp, readTemp, pid: PID, startReflow, elapsedTime, encValue, readReflowTime):
        self.lcd = lcd
        self.setTemp = setTemp
        self.readTemp = readTemp
        self.startReflow = startReflow
        self.encValue = encValue
        self.readReflowTime = readReflowTime
        self.pid = pid
        self.menuX = 0
        self.menuY = 0
        self.sinceLastBlink = 0
        self.cursorOn = False

        self.lastEncValue = 0
        self.wasError = False
        self.currentScreen = "main"
        self.selectedProfile = ""
        self.elapsedTime = elapsedTime

        self.mainMenuConstants()

    # Prints constants for running reflow
    def runningConstDisplay(self):
        self.lcd.clear()
        self.lcd.move_to(0, 0)
        self.lcd.putstr("Actual temp: ")
        self.lcd.move_to(0, 1)
        self.lcd.putstr("Set temp: ")
        self.lcd.move_to(0, 2)
        self.lcd.putstr("D: ")
        self.lcd.move_to(8, 2)
        self.lcd.putstr("Time: ")
        self.lcd.move_to(0, 3)
        self.lcd.putstr("PID: ")

    # Screen to be shown during reflow
    def reflowRunningDisplay(self):
        temp = self.readTemp()
        if type(temp) is not float:
            if not self.wasError: self.lcd.clear()
            self.lcd.move_to(0, 0)
            self.lcd.putstr(str(temp))
            self.wasError = True
            return
        if self.wasError:
            self.lcd.clear()
            self.runningConstDisplay()
            self.wasError = False
        self.lcd.move_to(14, 0)
        self.lcd.putstr(str(temp))
        self.lcd.move_to(10, 1)
        self.lcd.putstr("%.2f" % self.setTemp() + "  ")
        self.lcd.move_to(3, 2)
        self.lcd.putstr("%.2f" % self.pid.d)
        self.lcd.move_to(13, 2)
        self.lcd.putstr(str(self.elapsedTime()))
        self.lcd.putstr("/")
        self.lcd.putstr(str(self.readReflowTime()))
        self.lcd.move_to(5, 3)
        self.lcd.putstr("%.2f" % self.pid.pidValue + "  ")

    def mainMenuConstants(self):
        self.lcd.clear()
        self.lcd.move_to(0, 0)
        self.lcd.putstr("Gril v 1.1")
        self.lcd.move_to(0, 2)
        self.lcd.putstr("Leaded")
        self.lcd.move_to(10, 2)
        self.lcd.putstr("Lead free")
        self.lcd.move_to(0, 3)
        self.lcd.putstr("Gril temp: ")
        self.menuX = 0
        self.menuY = 2
        self.lcd.move_to(self.menuX, self.menuY)

    def mainMenu(self):
        if self.encValue() > self.lastEncValue:
            self.menuX = 10
            self.menuY = 2
            self.lastEncValue = self.encValue()
        elif self.encValue() < self.lastEncValue:
            self.menuX = 0
            self.menuY = 2
            self.lastEncValue = self.encValue()
        self.lcd.move_to(11, 3)
        self.lcd.putstr(str(self.readTemp()))
        self.lcd.move_to(self.menuX, self.menuY)
        if self.sinceLastBlink > 2:
            if self.cursorOn:
                self.lcd.putstr("L")
                self.cursorOn = False
                self.sinceLastBlink = 0
            else:
                self.cursorOn = True
                self.lcd.putAllBlack()
                self.sinceLastBlink = 0

    def confirmMenuConstants(self):
        self.lcd.clear()
        self.lcd.move_to(0, 0)
        if self.selectedProfile == "leaded":
            self.lcd.putstr("Leaded (temp, sec):")
        else:
            self.lcd.putstr("Pbfree (temp, sec):")
        self.lcd.move_to(0, 1)
        profile = Profile(self.readTemp, self.selectedProfile).readProfile()
        self.lcd.putstr(str(profile[0]) + str(profile[1]))
        self.lcd.move_to(0, 2)
        self.lcd.putstr(str(profile[2]) + str(profile[3]))
        self.lcd.move_to(0, 3)
        self.lcd.putstr("Ok")
        self.lcd.move_to(10, 3)
        self.lcd.putstr("Back")
        self.lcd.move_to(0, 3)
        self.menuX = 0
        self.menuY = 3
        gc.collect()

    def confirmMenu(self):
        if self.encValue() > self.lastEncValue:
            self.menuX = 10
            self.menuY = 3
            self.lastEncValue = self.encValue()
            self.lcd.move_to(self.menuX, self.menuY)
        elif self.encValue() < self.lastEncValue:
            self.menuX = 0
            self.menuY = 3
            self.lastEncValue = self.encValue()
            self.lcd.move_to(self.menuX, self.menuY)


    # this is to remove bad pixels which appear after some time
    def refreshAllPixels(self):
        self.lcd.clear()
        if self.currentScreen == "main":
            self.mainMenuConstants()
        elif self.currentScreen == "confirmation":
            self.confirmMenuConstants()
        elif self.currentScreen == "reflow":
            self.runningConstDisplay()

    def goToMainMenu(self):
        self.lcd.clear()
        self.mainMenuConstants()
        self.currentScreen = "main"
    def show(self, click):
        self.sinceLastBlink += 1
        if self.currentScreen == "main":
            if click:
                if self.menuX == 0:
                    self.currentScreen = "confirmation"
                    self.selectedProfile = "leaded"
                    self.confirmMenuConstants()
                    self.lcd.blink_cursor_on()
                elif self.menuX == 10:
                    self.currentScreen = "confirmation"
                    self.selectedProfile = "leadfree"
                    self.confirmMenuConstants()
                    self.lcd.blink_cursor_on()
            else:
                self.mainMenu()
        elif self.currentScreen == "reflow":
            self.reflowRunningDisplay()
        elif self.currentScreen == "confirmation":
            if click:
                if self.menuX == 0:
                    self.currentScreen = "reflow"
                    self.runningConstDisplay()
                    self.lcd.hide_cursor()
                    self.startReflow(self.selectedProfile)
                elif self.menuX == 10:
                    self.currentScreen = "main"
                    self.lcd.hide_cursor()
                    self.mainMenuConstants()
            else:
                self.confirmMenu()
        else:
            self.mainMenu()
