# djbb-midi-box
DIY midi box based on a raspberry pi pico in a 3d printed case, featuring 16 arcade button "pads", 3 knobs for controlling volume & FX, and multiple modes of operation.

**Features**: 
* 16 (non-velocity sensitive) buttons for sending midi messages
* Preset midi banks that can be re-mapped
  * Note: these mappings are per session. They will not be saved when the device powers off.
* Velocity control
* Repeat mode with optional note lock
  * With free or BPM sync (ROUGH bpm sync, I should say)

## Hardware Needed
* 1 Raspberry pi pico
* 1 OLED screen [use this for the code to work out of the box](https://www.aliexpress.com/item/32957309383.html?spm=a2g0o.order_list.0.0.4488194dIRto7O)
  * SSD1306
* 12 m3 nuts and bolts
* 16 arcade-style buttons
  * The shallower ones... like [these](https://www.aliexpress.com/item/4000751585184.html?spm=a2g0o.order_list.0.0.11481802rvdrTG) 
* 3 10k linear potentiometers
* 1 3D Printed case (see here)
* 2 little clicky buttons for the screen controls (like [these](https://www.amazon.com/TWTADE-Yellow-Orange-6x6x5mm-Tactile/dp/B07C7211PJ/ref=sr_1_18?crid=3IQJG5HKILGWG&keywords=push+button+small+breadboard&qid=1651343850&sprefix=push+button+small+breadboar%2Caps%2C90&sr=8-18))
* GET BTN DIMENSIONS ^^^
* 1 micro USB cable

**Note**: you should test everything before proceeding, especially if buying these alibaba parts.

## Pico setup
* Perform setup as described [here](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)
* Add code.py and the lib folder to the base directory of your pico
* If you aren't using the same screen as I noted above, you may have to alter code.py 

## Building
* Insert the buttons and pots into the front plate.
* Use the M3 bolts to secure the screen, but DONT TIGHTEN TOO HARD. I cracked like 3 screens before I learned this lesson.
* Wire the buttons and pots to the board
* INSERT TABLE - BTN TO WHICH PIN
* Wire the screen to the board
* INSERT WIRING GUIDE FOR SCREEN

## Operation
* Plug it into your computer
  * Tested on MacOS, Windows and iPadOS

General

Navigation / settings - Use the two nav buttons above the screen to change options within a screen. Press and hold one of the nav buttons and press the other to move screens in either direction (press and hold the left button and then click the right one to navigate to the next screen, or the opposite to go to the previous).
vol


Screen #1 (default)
