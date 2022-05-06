# djbb-midi-box
DIY midi box based on a raspberry pi pico in a 3d printed case, featuring 16 arcade button "pads", 3 knobs for controlling volume & FX, an OLED menu screen, and multiple modes of operation. Buildable for ~$30, with minimal tools (3D printer is the kicker here - you need one of these, or access to one).

## Features
* 16 (non-velocity sensitive) buttons for sending midi messages
* Preset midi banks that can be re-mapped
  * Note: these mappings are per session. They will not be saved when the device powers off.
* Velocity control
* Repeat mode with optional note lock
  * With free or BPM sync (ROUGH bpm sync, I should say)

## Hardware Needed
* (Tools) - Soldering Iron, Solder, M3 Allen Wrench, 3D Printer.
* 1 3D Printed case ([models here](https://www.printables.com/model/188671-djbb-arcade-button-midi-controller))
* 1 Raspberry pi pico
* 1 OLED screen [use this for the code to work out of the box](https://www.aliexpress.com/item/32957309383.html?spm=a2g0o.order_list.0.0.4488194dIRto7O)
  * SSD1306
* 12 m3 nuts and bolts
* 12 m3 heat inset nuts
* Some wire (helpful to have some solid core as well - can solder the buttons together easily)
* 16 arcade-style buttons
  * The shallower ones... like [these](https://www.aliexpress.com/item/4000751585184.html?spm=a2g0o.order_list.0.0.11481802rvdrTG) 
* 3 10k linear potentiometers
* 2 little clicky buttons for the screen controls (like [these](https://www.amazon.com/TWTADE-Yellow-Orange-6x6x5mm-Tactile/dp/B07C7211PJ/ref=sr_1_18?crid=3IQJG5HKILGWG&keywords=push+button+small+breadboard&qid=1651343850&sprefix=push+button+small+breadboar%2Caps%2C90&sr=8-18))
* 1 micro USB cable

**Overall Cost (not including shipping, assuming Alibaba parts, super rough estimate)**: ~ $20-30 bucks?

**Skills Required**: Basic 3d printing. Beginner-intermediate soldering (we are using most of the pins on the pico so it gets crowded).

**Note**: you should test everything before proceeding, especially if buying these alibaba parts.

## Pico setup
* Perform setup as described [here](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)
* Add code.py and the lib folder from this repo to the base directory of your pico
  * If you aren't using the same screen as I noted above, you may have to alter code.py 

## Building
* Insert the buttons and pots into the front plate.
* Use the M3 bolts to secure the screen, but DONT TIGHTEN TOO HARD. I cracked like 3 screens before I learned this lesson.
* Use a soldering iron to heat-inset the the m3 nuts into the bottom part of the case.
* Wire all of the button grounds together
  * Here it is useful to use some solid core wire, completely stripped. You can snake this around and solder each ground pin to it. It then becomes a rail that you can solder the screen, pots, and control button grounds to as well (instead of using a bunch of different ground pins on the pico). 

![Grnd Rail sm](https://user-images.githubusercontent.com/47721204/166162456-64432c59-6e11-4873-87d4-340109d0cc52.jpg)


* Wire the buttons and pots to the board.
* Wire the screen to the board

Reference [this pinout](https://datasheets.raspberrypi.com/pico/Pico-R3-A4-Pinout.pdf) diagram

**Buttons wiring**
|GP2|GP3|GP4|GP5|
|---|---|---|---|
|GP0|GP1|GP8|GP9|
|GP10|GP11|GP12|GP13|
|GP14|GP15|GP16|GP17|

**Pots wiring**
|Pot 1 (Left)|Pot 2 (Mid)|Pot 3 (Right)|
|---|---|---|
|GP26|GP27|GP28|

**Control Buttons**
|Btn Left|Btn Right|
|---|---|
|GP20|GP21|

**Screen**
|SDA|SCL|GND|VCC|
|---|---|---|---|
|GP6|GP7|Any ground pin|Pin 36 (power)|

## Operation
* Plug it into your computer
  * Tested on MacOS, Windows and iPadOS

**General Operation**
![1 Pic Guide@0 5x](https://user-images.githubusercontent.com/47721204/166162447-f6612633-b3dd-44f2-8d21-a83da9dc8450.jpg)


**Screens Guide**
![scrn guid@0 5x](https://user-images.githubusercontent.com/47721204/166162453-ea4f6f45-ff22-409b-90e7-eaad3359af39.jpg)

**Fun things to try**
I created this to use with drums, but it can be fun with melodic stuff too. Try turning repeats on with repeat falloff set to 0 (Pot 2 all the way to the left). 

Now hold both nav buttons, and press a note button. It should now be repeating forever at the repeat speed (knob 3). Do this again with other notes to make a lil looper.

## Customization
You can open and edit code.py to your liking. I put some run options near the top of the file. These are constants that other parameters reference, so you can mess with these to easily change some of the general settings.

## Enhancements and Optimization Ideas

* Some sort of preset system maybe? So saving custom mapped midi bank values, etc.
* More midi FX - Pot 2 is underutilized
* DAW BPM Sync? No idea if this is possible.

Not sure if it's worth doing until this thing gets bigger and more unwieldy, but would be nice to..

* Refactor code into multiple files. Many of the constants could be separated into another file to make the whole deal easier to read.
 * Run options, midi dictionaries, etc.
* Heck, maybe each screen should be it's own file.
