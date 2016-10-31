# SH1106 SPI OLED Driver

The original README(s) from the SSD1306 project(s) are missing here. If you are looking
for information on how to get everything to work then please have a look at those.

[rm-hull/ssd1306](https://github.com/rm-hull/ssd1306)
The original oled project. SSD1306/SH1106 via I2C

[rogerdahl/ssd1306](https://github.com/rogerdahl/ssd1306)   Adding SPI


## What's here

The original project have some nice demoes but when you get the urge to display
more than a single page, perhaps with some nice fades, then a framework to deal
with the boring stuff would be nice to have. Such a framework is what is added 
here together with a demo showing some assorted machine info.

Two new python scripts have been added:

### oled/sequencer.py

Contains the sequencer and also two base classes to be used by posters (the views). 
The sequencer fetches new posters to display from the client script so both 
the actual posters available and the order they should appear in is under
the control of the client script.

### examples/poster_demo.py

Loads some machine info posters from examples/posters and starts the sequencer.
[a little video of the poster_demo](https://cloud.githubusercontent.com/assets/12825543/19840216/9f69809e-9ef1-11e6-9346-5226ca950a00.gif)
The individual demo posters are designed to occupy only half the display width. 
This is just an odd design decision for the demo, they can be of any width.

## Running

Do the setups and package installs as detailed in the original README(s).
Then its just a matter of launching poster_demo.py. There is also a minimalistic
systemd script to get the demo to start at boot time on a raspberry pi.

It is possible to run the demo on a linux PC (i.e. without a SPI display) by using 
gstreamer as a-sort-of real-time image viewer. Start the demo with a filename as argument
and then launch the following gstreamer pipeline:
>gst-launch-1.0 multifilesrc loop=true start-index=0 stop-index=0 \
>location=<filename> ! decodebin ! identity sleep-time=10000 ! \
>videoconvert ! autovideosink


## Disclaimers

All drawing manipulations are done in software which then by definition also includes 
the scrolling operation. Since posters are allowed to go wild with screen updates, 
scrolling in hardware haven't been an option (in case its even possible).

Only a SPI display have been tested. The lower bandwidth on a I2C bus might 
be a problem, but be aware that I2C hasn't been tried at all. 
The scripts here were made for a SH1106 display connected via SPI.

There is always something that breaks in strange ways but the demo here should 
run more or less out of the box with python 2.7 on a raspberry pi 3. The distro
tested is Arch so there might be some adjustments needed for e.g. raspbian or other distroes.

