from machine import Pin, SPI, I2C
import uasyncio


encPlus = Pin(21, Pin.IN)
encPlusLastState = 0
encPlusNewState = 0
encMinus = Pin(20, Pin.IN)
encButton = Pin(19, Pin.IN) #Pressed when low


def handlePlusIrq(pin :Pin):
    global encPlusNewState
    encPlusNewState = pin.value()
# def handleMinusIrq(pin :Pin):
#     print(pin.value())

encPlus.irq(handler=handlePlusIrq)
# encMinus.irq(trigger=Pin.IRQ_RISING,handler=handleMinusIrq)

relay = Pin(3, Pin.OUT)

###############################################
def readRotary():
    global encPlusNewState
    global encPlusLastState
    while (True):
        if (encPlusNewState != encPlusLastState):
            encPlusLastState = encPlusNewState
            if (encPlusNewState == 0 and encMinus.value() == 1):
                # turn right
                print("Turning right")
            elif (encPlusNewState == 1 and encMinus.value() == 0):
                # turn right
                print("Turning right")
            elif (encPlusNewState == 1 and encMinus.value() == 1):
                # turn left
                print("Turning left")
            else:
                # turn left
                print("Turning left")


def pretify(cas):
    if cas < 10:
        return str("0" + str(cas))
    else:
        return str(cas)


loop = uasyncio.get_event_loop()
uasyncio.create_task(readRotary())

loop.run_forever()
