# DIY-raspberrypi-pico usb midifighter
This is a project of programming the usb midi controller using a raspberry pi pico, 16 arcade buttons, and a joystick, and a slide potentiometer. It looks like this.

![IMG_0386](https://user-images.githubusercontent.com/30145956/132351004-bbbbf3f4-c9a3-4ce9-83a4-659cbd0b7c89.JPG)


The project code mainly using the code from here
<https://learn.adafruit.com/raspberry-pi-pico-led-arcade-button-midi-controller-fighter/coding-the-raspberry-pi-pico-midi-controller>

also im referencing other codes from other places because I'm using different components such as a analog joystick, slide potentiometer etc.

here are the links im referencing
- for knob functions : https://www.notion.so/midi-3d7e1cd3b45641999254624df3f391de#fb3c65681f5e41579676120b0cb622f5
- for joysticks : https://www.tomshardware.com/how-to/raspberry-pi-pico-joystick

## What it does
not only this midi fighter controller has 16 arcade midi buttons, using a joystick you can shift an octave and reach all 128 keys. also by tilting the joystick horizontally you can change the midi channel, thus be able to change instruments. when tilting the joystick, an rgb led will light up as an indecation of the channel and the octave you are in. 

![1_0_GIF_0](https://user-images.githubusercontent.com/30145956/132369124-7f9bae9c-7a06-486a-bec1-ac9cabf5ca52.gif)

## How to make this

**Requirements:**
  - 16 arcade buttons. I used a 30mm buttons for this 
  - raspberry pi pico
  - 1 joystick. I used an analog joystick because it felt better
  - 1 rgb led and a white led
  - liniar potentiometer for slider midi control

> the skimatics will be like this. I didn't wire the rest of the buttons but it will be connected in order on the following remaining gpio.

![Untitled Sketch_bb](https://user-images.githubusercontent.com/30145956/132359437-05dff6b0-a847-43bd-a257-40841fb6bcbd.png)

the case that i made looks like this. (I'll share the file, but in retrospect i should have located the bottom raspberry pi pico screws location to a different place.)

[acrylic case.pdf](https://github.com/Thenextpage/diy-raspberrypi-pico-midifighter-project/files/7122417/4add7cef-6b07-41a8-b77b-67100d3bae9c.dwg-0001.pdf)
![ef](https://user-images.githubusercontent.com/30145956/132366060-8b058fc0-c745-4bb4-a8cf-44fdc6c8b082.png)

after you make like this and making the case, you can install the main code into the raspberry pi as a main.py, and after adding these libraries into the pico, it will automatically works like a midi fighter after you plug the micro usb.

- adafruit_circuitplayground
- adafruit_midi
- adafruit_rgbled.mpy
- neopixel.mpy
- simpleio.mpy
  
## Development plans
  
I'm planning to utilize the joystick button press to enter the CC mode, which is the control change mode. Some DAWs like ableton will treat midi note signals and the control change signals differently, so it will give the user more control in performance.
