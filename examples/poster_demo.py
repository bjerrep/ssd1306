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
import subprocess

from oled.sequenser import Poster, ThreadedPoster, Sequenser

yappi_profiling = False
if yappi_profiling:
    import yappi


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
        del draw

    def get_image(self):
        return self.image


def gett():
    return psutil.cpu_percent(2, percpu=True)

# see also sys_info.py


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

            ret = subprocess.check_output(
                'top -d%f -bn2 | grep "Cpu[0123]" | tail -n4 | '
                'awk \'{print $3}\' | cut -d/ -f1' %
                self.interval, shell=True)
            percentages = [float(x) for x in ret.split()]

            self.interval = 1
            x = 0
            for cpu in percentages:
                bar_height = self.height - 2 * self.bar_space_vert
                cpu_bar = 1 + bar_height * (cpu / 100.0)
                draw.rectangle((x + self.bar_air,
                               self.bar_space_vert + bar_height - cpu_bar) +
                               (x + self.bar_width - self.bar_air,
                               self.height - self.bar_space_vert),
                               'white', 'white')
                x += self.bar_width
                time.sleep(0.001)
            self.image = image
            self.new_image_is_ready()
            del image
            del draw

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
                del image
                del draw
                self.new_image_is_ready()
            time.sleep(0.1)

    def get_image(self):
        return self.image


def start_yappi():
    print('yappi running')
    yappi.set_clock_type('wall')
    yappi.start()


def stop_yappi():
    """
    Use seq.set_timing(0, 1, 0.040) to exercise the fading

    see https://github.com/pantsbuild/pants/wiki/Debugging-Tips:\
    -multi-threaded-profiling-with-yappi
    """
    yappi.stop()
    print('writing /tmp/yappi./tmp/yappi.callgrind')
    stats = yappi.get_func_stats()
    stats.save('/tmp/yappi.callgrind', 'callgrind')


# This can be as dynamic as needed, here the static list is just
# traversed forever
posters = [LargeStaticText(size), Clock(size), CpuLoad(size)]
index = -1


def get_next():
    global index
    index += 1
    return posters[index % len(posters)]


def launch():
    try:
        if len(sys.argv) > 1:
            # add a filename argument to get rendering to a file
            seq = Sequenser(size, get_next, sys.argv[1])
        else:
            seq = Sequenser(size, get_next)

        seq.set_timing(3, 5, 0.040)  # 3 secs and then a speedy scroll
        # seq.set_timing(0, 1, 0.040)  # continous scrolling, not quite there
        while seq.isAlive():
            seq.join(0.1)

    except KeyboardInterrupt:
        seq.terminate()

    for p in posters:
        p.terminate()


def launch_with_yappi():
    try:
        seq = Sequenser(size, get_next)

        start_yappi()
        seq.set_timing(0, 1, 0.040)
        time.sleep(60)
        seq.terminate()
        stop_yappi()

        while seq.isAlive():
            seq.join(0.1)
    except KeyboardInterrupt:
        seq.terminate()

    for p in posters:
        p.terminate()


if yappi_profiling:
    launch_with_yappi()
else:
    launch()
