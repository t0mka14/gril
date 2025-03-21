# gril
A gril control unit for reflowing pcbs. The project consists of two parts - Micropython code for Rpi Pico and one PCB. \
**PCB**\
Apart from the Pico there is MAX31855 that converts temperature of thermocouple glued to the grill plate and sends it over SPI to PICO. Then there is one mosfet to control external SSR and linear stabilizer as the input voltage is 12V. The whole device is controlled using rotary encoder connected to GPIO pins 19-21. The encoder button goes to 19. The display is any 16x4 I2C LCD.\
**Code**\
The code uses two Asyncio loops, one for controlling temperature and on for displaying stuff. If you want to tune the PID controller, you can change parameters on line 92 in gril.py
