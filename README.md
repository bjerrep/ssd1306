# SH1106 SPI OLED Driver

The original README(s) from the SSD1306 project(s) are missing here. If you are looking
for information on how to get everything to work then please have a look at those.

[rm-hull/ssd1306](https://github.com/rm-hull/ssd1306)
The original oled project. SSD1306/SH1106 via I2C

[rogerdahl/ssd1306](https://github.com/rogerdahl/ssd1306)   Adding SPI


## What's here

The original project have some nice demoes but when you get the urge to display
more than a single page, perhaps with some nice fades, then a framework to deal
with the boring stuff would be nice to have. This is what is added here.

Two new python scripts have been added:

### oled/sequencer.py

Contains the sequencer and also two base classes to be used by posters (the views). 
The sequencer fetches new posters to display from the client script so both 
the actual posters available and the order they should be appear in is under
the control of the client script.

### examples/poster_demo.py

Contains three demo posters and starts the sequencer. 

## Running

Do the setups and package installs as detailed in the original README(s).
Then its just a matter of launching poster_demo.py

It is possible to run the demo on a linux PC (i.e. without a SPI display) by using 
gstreamer as a real-time image viewer. Look in poster_demo.py for how to do it. 

## Disclaimers

All drawing manipulations are done in software. Unfortunately this means that a
r-pi-3 cpu core is quite busy when fading and it will occasionally stutter as in
beeing not perfect. Somebody should look into this . .

Only a SPI display have been tested. The lower bandwidth on a I2C bus might 
be a problem, but be aware that I2C hasn't been tried at all. 
The scripts here were made for a SH1106 display connected via SPI.

There is always something that breaks in strange ways but the demo here should 
run more or less out of the box with both python 2.7 and 3.

The font used in the demo is DroidSans.ttf, chances are that you either need to 
install it or use another one.