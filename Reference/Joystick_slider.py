import board
from analogio import AnalogIn
import usb_hid
import time


xAxis = AnalogIn(board.A1)
yAxis = AnalogIn(board.A0)
sAxis = AnalogIn(board.A2)

in_min,in_max,out_min,out_max = (0, 65000, -10, 10)
filter_joystick_deadzone = lambda x: round(((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min),2 ) if abs(x-33500) > 1000 else 0


while True:
    x_offset = filter_joystick_deadzone(xAxis.value) * -1 #Invert axis
    y_offset = filter_joystick_deadzone(yAxis.value)

    print(x_offset,y_offset,sAxis.value)
    time.sleep(0.1)

