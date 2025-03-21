from machine import Pin, SPI, I2C
import uasyncio
from lib.regulator import PID
from lib.max31855 import MAX31855
from lib.pico_i2c_lcd import I2cLcd
from src.Display import Display
from src.Profile import Profile
cs = Pin(13, Pin.OUT)
spi = SPI(1, 10_000_000, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
tempSensor = MAX31855(spi, cs)



I2C_ADDR = 0x27
I2C_NUM_ROWS = 4
I2C_NUM_COLS = 20
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)


beeperPin = Pin(5, Pin.OUT)
encPlus = Pin(21, Pin.IN)
encPlusLastState = 0
encPlusNewState = 0
encMinus = Pin(20, Pin.IN)
encButton = Pin(19, Pin.IN)  # Pressed when low
encValue = 0
buttonPressed = False
setTemp = 0
elapsedTime = 0

relay = Pin(3, Pin.OUT)


profile = None

##############################################
#Rotary encoder methods
def handlePlusIrq(pin: Pin):
    global encPlusNewState
    encPlusNewState = pin.value()
def readTestRotary(pin: Pin):
    global encPlusLastState
    global encValue
    if (pin.value() != encPlusLastState):
        encPlusLastState = pin.value()
        if (pin.value() == 0 and encMinus.value() == 1):
            # turn right
            encValue += 5
        elif (pin.value() == 1 and encMinus.value() == 0):
            # turn right
            encValue += 5
        elif (pin.value() == 1 and encMinus.value() == 1):
            # turn left
            encValue -= 5
        else:
            # turn left
            encValue -= 5
def readButtonRotary(pin :Pin):
    global buttonPressed
    buttonPressed = True

encPlus.irq(handler=readTestRotary)
encButton.irq(handler=readButtonRotary, trigger = Pin.IRQ_FALLING)
def readEncoderValue():
    return encValue
def readSetTemp():
    return setTemp
def readElapsedTime():
    return elapsedTime
def readReflowTime():
    if profile is not None:
        return profile.profile[-1][1]
    else:
        return 0
##########################################################
def readTemperature():
    try:
        return tempSensor.read()
    except Exception as e:
        return e

#callback from display!
def startReflow(type):
    global profile
    profile = Profile(readTemperature,type)
    uasyncio.create_task(tempControl())

##############################################


pid = PID(readTemperature,P=2, I=0.7, D=0.1)

display = Display(lcd,readSetTemp,readTemperature,pid, startReflow, readElapsedTime,readEncoderValue, readReflowTime)

loop = uasyncio.get_event_loop()
###############################################


def tempControl():
    global setTemp
    global elapsedTime
    period = 1
    elapsedTime = 0
    while (profile.profile[-1][1] + 30 > elapsedTime):
            setTemp = profile.calculateTempForTime(elapsedTime)
            onTime = pid.getOnTime(setTemp)
            if onTime == 1:
                relay.value(1)
                await uasyncio.sleep(period)
            elif onTime == 0:
                relay.value(0)
                await uasyncio.sleep(period)
            else:
                relay.value(1)
                await uasyncio.sleep(onTime)
                relay.value(0)
                await uasyncio.sleep(period - onTime)
            ####beep when finished
            if (elapsedTime > profile.profile[-1][1] and elapsedTime < profile.profile[-1][1] + 5):
                beeperPin.value(1)
            else:
                beeperPin.value(0)
            elapsedTime += 1
    relay.value(0)
    display.goToMainMenu()


def displayControl():
  global buttonPressed
  displayClearTimer = 0
  while(True):
    display.show(buttonPressed)
    buttonPressed = False
    displayClearTimer += 200
    if displayClearTimer > 5*60000:
        display.refreshAllPixels()
        displayClearTimer = 0
    await uasyncio.sleep_ms(200)




uasyncio.create_task(displayControl())


# uasyncio.create_task(readRotary())
loop.run_forever()
