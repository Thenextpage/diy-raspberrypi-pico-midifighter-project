import time
import board
import busio
import digitalio
import usb_midi
import adafruit_midi
from adafruit_midi.note_on          import NoteOn
from adafruit_midi.note_off         import NoteOff
from simpleio import map_range
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction
from adafruit_midi.control_change import ControlChange 
import math
import adafruit_rgbled

#setup analog joystick and slider inputs
xAxis = AnalogIn(board.A1)
yAxis = AnalogIn(board.A0)
sAxis = AnalogIn(board.A2)
led=adafruit_rgbled.RGBLED(board.GP0,board.GP1,board.GP2)
ledw = digitalio.DigitalInOut(board.GP3)
ledw.direction = digitalio.Direction.OUTPUT

note_states = [False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False] #  note states
midi_notes = [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51] #  array of default MIDI notes
ledcolor=[[255,0,0],[255,80,0],[255,255,0],[0,255,0],[0,0,255],[0,100,255],[100,0,255],[255,255,255]]
ledwcolor=[[255,0,0],[255,80,0],[255,255,0],[0,255,0],[0,0,255],[0,100,255],[100,0,255],[255,255,255],[255,0,0],
           [255,80,0],[255,255,0],[0,255,0],[0,0,255],[0,100,255],[100,0,255],[255,255,255],[255,0,0],[255,80,0]]
cc_list=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
c_num=0
ledx_number=0
ledy_number=0
ledw_number=0
cc_value=[0,0]
last_cc_value=[0,0]
midi_range = 0
xswitch=0
yswitch=0

in_min,in_max,out_min,out_max = (0, 65000, -10, 10)

def range_index(ctl, ctrl_max, old_idx, offset):
    if (ctl + offset > 65535) or (ctl + offset < 0):
        offset = 0
    idx = int(map_range((ctl + offset) & 0xFF00, 1200, 65500, 0, ctrl_max))
    if idx != old_idx:  # if index changed, adjust hysteresis offset and set flag offset is 25% of the control slice (65536/ctrl_max)
        offset = int(0.25 * sign(idx - old_idx) * (65535 / ctrl_max)) # edit 0.25 to adjust slices
    return idx, offset

def sign(x):  # determine the sign of x
    if x >= 0:
        return 1
    else:
        return -1

filter_joystick_deadzone = lambda x: round(((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min),1 ) if abs(x-33500) > 20000 else 0

#  MIDI setup as MIDI out device
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1])
 
#  button pins, all pins in order skipping GP15 (Note that GP 6 is being used instead of 26 for analog input)
note_pins = [board.GP19, board.GP20, board.GP21, board.GP22, board.GP14, board.GP16, board.GP17, board.GP18, board.GP10, board.GP11, board.GP12, board.GP13, board.GP6, board.GP7, board.GP8, board.GP9]
note_buttons = []
 
for pin in note_pins:
    note_pin = digitalio.DigitalInOut(pin)
    note_pin.direction = digitalio.Direction.INPUT
    note_pin.pull = digitalio.Pull.UP
    note_buttons.append(note_pin)

clock = time.monotonic() #  time.monotonic() device

led.color=(255,0,0)
time.sleep(0.3)
led.color=(0,255,0)
time.sleep(0.3)
led.color=(0,0,255)
time.sleep(0.3)
ledw.value=True
led.color=(0,0,0)
time.sleep(0.3)
ledw.value=False

while True:   
    for i in range(16):    #  MIDI input
        buttons = note_buttons[i]
 
        if not buttons.value and note_states[i] is False:       #  if button is pressed...
            midi.send(NoteOn(midi_notes[i],120,channel=5))
            note_states[i] = True
            
        if buttons.value and note_states[i] is True:        #  if the button is released...
            midi.send(NoteOff(midi_notes[i],120,channel=5))
            note_states[i] = False
            
    #read knob values
    cc_value = range_index(sAxis.value,128,cc_value[0],cc_value[1])
    cc_list.append(cc_value[0])
    cc_list.pop(0)
    avgcc_val = round(sum(cc_list)/30)
    
    if avgcc_val != last_cc_value[0]:  # only send if it changed Form a MIDI CC message and send it:
        midi.send(ControlChange(1,avgcc_val))
        last_cc_value = cc_value
        
    x_offset = filter_joystick_deadzone(xAxis.value)  *-1       
    y_offset = filter_joystick_deadzone(yAxis.value)  *-1    #Invert axis
    
    if x_offset > 6:
        if xswitch == 1 or midi_range>3:
            continue
        for y in range(16):
            midi.send(NoteOff(midi_notes[y], 120))
            note_states[y] = False
        midi_notes = [x+16 for x in midi_notes]
        midi_range+=1
        ledx_number+=1
        led.color=(ledcolor[ledx_number][0],ledcolor[ledx_number][1],ledcolor[ledx_number][2])
        xswitch = 1
        
    if x_offset < -6:
        if xswitch == 1 or midi_range<-1:
            continue
        for y in range(16):
            midi.send(NoteOff(midi_notes[y], 120))
            note_states[y] = False
        midi_notes = [x-16 for x in midi_notes]
        midi_range-=1
        ledx_number-=1
        led.color=(ledcolor[ledx_number][0],ledcolor[ledx_number][1],ledcolor[ledx_number][2])
        xswitch = 1
                    
    if -6<= x_offset <= 6:
        xswitch=0
        if yswitch==0:
            led.color=(0,0,0)
    
    if y_offset > 6:
        if yswitch == 1 or c_num>14:
            continue
        for y in range(16):
            midi.send(NoteOff(midi_notes[y], 120))
            note_states[y] = False
        c_num+=1
        ledy_number+=1
        led.color=(ledwcolor[ledy_number][0],ledwcolor[ledy_number][1],ledwcolor[ledy_number][2])
        ledw.value=True
        midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1],out_channel=c_num)
        yswitch = 1
            
    if y_offset < -6:
        if yswitch == 1 or c_num<1:
            continue
        for y in range(16):
            midi.send(NoteOff(midi_notes[y], 120))
            note_states[y] = False
        c_num-=1
        ledy_number-=1
        led.color=(ledwcolor[ledy_number][0],ledwcolor[ledy_number][1],ledwcolor[ledy_number][2])
        ledw.value=True
        midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1],out_channel=c_num)
        yswitch = 1

    if -6<= y_offset <= 6:
        yswitch=0
        if xswitch==0:
            led.color=(0,0,0)
        ledw.value=False
