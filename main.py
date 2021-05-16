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
import adafruit_midi  # MIDI protocol encoder/decoder library
from adafruit_midi.control_change import ControlChange 
import math
from adafruit_circuitplayground import cp

#setup analog joystick and slider inputs
xAxis = AnalogIn(board.A1)
yAxis = AnalogIn(board.A0)
sAxis = AnalogIn(board.A2)

cc_value=[0,0]
last_cc_value=[0,0]
in_min,in_max,out_min,out_max = (0, 65000, -10, 10)

def range_index(ctl, ctrl_max, old_idx, offset):
    if (ctl + offset > 65535) or (ctl + offset < 0):
        offset = 0
    idx = int(map_range((ctl + offset) & 0xFF00, 1200, 65500, 0, ctrl_max))
    if idx != old_idx:  # if index changed, adjust hysteresis offset and set flag
                        # offset is 25% of the control slice (65536/ctrl_max)
        offset = int(0.25 * sign(idx - old_idx) * (65535 / ctrl_max))
        # edit 0.25 to adjust slices
    return idx, offset

def sign(x):  # determine the sign of x
    if x >= 0:
        return 1
    else:
        return -1

filter_joystick_deadzone = lambda x: round(((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min),1 ) if abs(x-33500) > 1000 else 0
   
#  MIDI setup as MIDI out device
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)
 
#  button pins, all pins in order skipping GP15 (Note that GP 6 is being used instead of 26 for analog input)
note_pins = [board.GP6, board.GP7, board.GP8, board.GP9, board.GP10, board.GP11,
             board.GP12, board.GP13, board.GP14, board.GP16, board.GP17,
             board.GP18, board.GP19, board.GP20, board.GP21, board.GP22]
 
note_buttons = []
 
for pin in note_pins:
    note_pin = digitalio.DigitalInOut(pin)
    note_pin.direction = digitalio.Direction.INPUT
    note_pin.pull = digitalio.Pull.UP
    note_buttons.append(note_pin)
 
#  note states
note_states = [False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False]
 
#  default midi number
#midi_num = 60
#  default MIDI button
#button_num = 0
#  default MIDI button position
#button_pos = 0
#  time.monotonic() device
clock = time.monotonic()

#  array of default MIDI notes

midi_notes = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75]
midi_range = 0
xswitch=0
yswitch=0
cc_list=[0,0,0,0,0,0,0,0,0,0]

while True:
 
    
    #  MIDI input
    for i in range(16):
        buttons = note_buttons[i]
        #  if button is pressed...
        if not buttons.value and note_states[i] is False:
            midi.send(NoteOn(midi_notes[i], 120))
            note_states[i] = True
        #  if the button is released...
        if buttons.value and note_states[i] is True:
            midi.send(NoteOff(midi_notes[i], 120))
            note_states[i] = False
            
        #read knob values
    cc_value = range_index(sAxis.value,128,cc_value[0],cc_value[1])
    cc_list.append(cc_value[0])
    cc_list.pop(0)
    avgcc_val = round(sum(cc_list))/10)

    if avgcc_val != last_cc_value[0]:  # only send if it changed
        # Form a MIDI CC message and send it:
        midi.send(ControlChange(1,avgcc_val))
        last_cc_value = cc_value
        
    x_offset = filter_joystick_deadzone(xAxis.value) * -1 #Invert axis
    y_offset = filter_joystick_deadzone(yAxis.value)
    if x_offset > 0.7:
        if xswitch == 1 or midi_range>3:
            continue
        for y in range(16):
            midi.send(NoteOff(midi_notes[y], 120))
            note_states[y] = False
        midi_notes = [x+12 for x in midi_notes]
        midi_range+=1
        xswitch = 1
    elif x_offset < -0.7:
        if xswitch == 1 or midi_range<-3:
            continue
        for y in range(16):
            midi.send(NoteOff(midi_notes[y], 120))
            note_states[y] = False
        midi_notes = [x-12 for x in midi_notes]
        midi_range-=1
        xswitch = 1
    else:
        if xswitch==0:
            continue
        xswitch=0
                      
        #  update arcade button's MIDI note
        #  allows you to check note while you're adjusting it
