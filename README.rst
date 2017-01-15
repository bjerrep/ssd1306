
ssd1306 playground
==================

This is a fork of the rm-hull/luma.oled project intended for general fooling around. The upstream have all the latest stuff, extensive documentation etc so if you're looking for a place to start then have a look there.

poster_demo
-----------
There now is a similar demo in upstream so this one here might be a little dated. The intention is to have a machine info display running on a rpi. There is also a rudimentary systemd script so once a rpi is hooked up to a display it should be quite simple to have the poster_demo running at boot. For a headless rpi this is a must have :-)

.. image:: https://cloud.githubusercontent.com/assets/12825543/19840216/9f69809e-9ef1-11e6-9346-5226ca950a00.gif
   :alt: posterdemo

**oled/sequencer.py**: Contains the sequencer and also two base classes to be used by posters (the views). 
The sequencer fetches new posters to display from the client script so both 
the actual posters available and the order they should appear in is under
the control of the client script.

**examples/poster_demo.py**: Loads some machine info posters from examples/posters and starts the sequencer.
The individual demo posters are designed to occupy only half the display width. 
This is just an odd design decision for the demo, they can be of any width.

It is possible to run the demo on a linux PC (i.e. without a SPI display) by using 
gstreamer as a-sort-of real-time image viewer. Start the demo with a filename as argument
and then launch the following gstreamer pipeline:

.. code-block::

  gst-launch-1.0 multifilesrc loop=true start-index=0 stop-index=0 location=filename ! decodebin ! identity sleep-time=10000 ! videoconvert ! autovideosink

Upstream have built-in emulators and an animated gif recorder. But this is still a handy gstreamer hack to have in the toolbox.


television
----------

Everybody wants a oled tv so here it is. Its impressive that anything can even be recognized with a 128*64 resolution in one color when playing a video, but it sort of can:

.. image:: https://cloud.githubusercontent.com/assets/12825543/21967215/f579453c-db82-11e6-8977-390276c23fe3.gif
   :alt: television_demo

The television demo uses gstreamer for the heavy lifting so thats brings in a fair amount of new packages to install. Don't do this if diskspace is low and be aware that a little tinkering might be needed as well. The television demo can play videos, online http live feeds and show the test patterns from the gstreamer videotestsrc. The movie above is from divx.com and recorded with the 'gifanim' display driver. A quad core rpi is rather loaded when decoding and rescaling e.g. mp4 streams so less powerfull rpis might require somewhat lighter encodings. A display with a depth of more than one bit, a slightly higher resolution and perhaps even some colors then it will be time to add some sound...


Disclaimers
-----------

Only a SPI sh1106 display have been tested.

There is always something that breaks in strange ways but the demo here should 
run more or less out of the box with python 2.7 on a raspberry pi 3. The distro
tested is Arch so there might be some adjustments needed for e.g. raspbian or other distroes.
