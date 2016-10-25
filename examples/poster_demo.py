#!/usr/bin/env python

# Running without a real display:
# it is possible to specify a filename to the the sequenser and then let the
# following gstreamer pipeline reload the image in a video sink. None of the
# image viewers that support autoreloading seems to be able to match this.
"""
gst-launch-1.0 multifilesrc loop=true start-index=0 stop-index=0 \
location=<file name.png> ! decodebin ! identity sleep-time=10000 ! \
videoconvert ! autovideosink
"""

import psutil
import sys
import time

from oled.sequenser import Poster, ThreadedPoster, Sequenser


if __name__ == '__main__':
    w = 128
    h = 64
    size = (w, h)

    class LargeStaticText(Poster):
        def __init__(self, size):
            super(LargeStaticText, self).__init__(size)
            self.width = 150
            self.image, draw = self.get_new_image_and_canvas()
            pos = self.text(draw, (10, 10), 'github: cbjerre/ssd1306')
            pos = self.text(draw, pos, 'rm-hull/ssd1306', 'large')
            self.text(draw, pos, 'rogerdahl/ssd1306', 'small')

        def get_image(self):
            return self.image

    # see also sys_info.py
    #
    class CpuLoad(ThreadedPoster):
        bar_width = 20
        bar_air = 8
        bar_space_vert = 10

        def __init__(self, size):
            super(CpuLoad, self).__init__(size, self.get_cpu_load_and_redraw)
            self.width = self.bar_width * psutil.cpu_count()
            self.image = self.get_new_image()
            self.interval = 0.1

        def get_cpu_load_and_redraw(self):
            while not self.is_terminated():
                image, draw = self.get_new_image_and_canvas()

                self.text(draw, (self.width/2, 10), 'CpuLoad', 'small', 'middle')

                # better spawn a process that will be able to use another cpu core
                percentages = psutil.cpu_percent(self.interval, percpu=True)

                # after some time cpu_percent() seems to ignore the interval
                # and go flat out. Add a little cpu breathing space
                time.sleep(0.1)

                self.interval = 2
                x = 0
                for cpu in percentages:
                    time.sleep(0.001)
                    bar_height = self.height - 2 * self.bar_space_vert
                    cpu_bar = bar_height * cpu / 100.0
                    draw.rectangle((x + self.bar_air,
                                    self.bar_space_vert + bar_height - cpu_bar) +
                                   (x + self.bar_width - self.bar_air,
                                    self.height - self.bar_space_vert),
                                   'white', 'white')
                    x += self.bar_width
                    time.sleep(0.001)
                self.image = image
                self.new_image_is_ready()

        def get_image(self):
            return self.image

    class Clock(ThreadedPoster):
        def __init__(self, size):
            super(Clock, self).__init__(size, self.get_clock)
            self.image = self.get_new_image()
            self.time = ''

        def get_clock(self):
            while not self.is_terminated():
                new_time = time.strftime('%H:%M:%S', time.gmtime())
                if new_time != self.time:
                    self.time = new_time
                    image, draw = self.get_new_image_and_canvas()
                    self.text(draw, (64, 32), new_time, 'huge', 'middle')
                    self.image = image
                    self.new_image_is_ready()
                    time.sleep(0.5)
                else:
                    time.sleep(0.1)

        def get_image(self):
            return self.image

    posters = [LargeStaticText(size), CpuLoad(size), Clock(size)]
    index = -1

    # This can be as dynamic as needed, here the static list is just
    # traversed forever
    def get_next():
        global index
        index += 1
        return posters[index % len(posters)]

    try:
        if len(sys.argv) > 1:
            # add a filename argument to get rendering to a file
            seq = Sequenser(size, get_next, sys.argv[1])
        else:
            seq = Sequenser(size, get_next)

        # seq.set_timing(5, 6, 0.010)
        seq.set_timing(5, 1, 0.020)
        while seq.isAlive():
            seq.join(0.1)
    except KeyboardInterrupt:
        seq.terminate()

    for p in posters:
        p.terminate()
