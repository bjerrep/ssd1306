#!/usr/bin/env python

import sys
import time
from oled.sequenser import Sequenser
from demo_opts import device
import argparse

sys.path.append('posters')
import uptime
import cpu
import disk
import net
import memory

parser = argparse.ArgumentParser()
parser.add_argument('--image-file', type=str,
                    help='Imagefile for gstreamer')
parser.add_argument('--yappi', dest='yappi', action='store_true',
                    default=False, help='Timeboxed yappi run')
parser.add_argument('--poster-width', type=int,
                    default=64, help='Anything but 64 is experimental')

args, unknown = parser.parse_known_args()

if args.yappi:
    import yappi


def start_yappi():
    print('yappi running')
    yappi.set_clock_type('wall')
    yappi.start()


def stop_yappi():
    """
    Use seq.set_timing(0, 1, 0) to fade at full tilt

    see https://github.com/pantsbuild/pants/wiki/Debugging-Tips:\
    -multi-threaded-profiling-with-yappi
    """
    import yappi
    yappi.stop()
    print('writing /tmp/yappi.callgrind')
    stats = yappi.get_func_stats()
    stats.save('/tmp/yappi.callgrind', 'callgrind')


class Posters:
    posters = []
    index = -1

    def construct(self, size):
        self.posters.append(uptime.TimeAndUptime(size))
        self.posters.append(net.Summary(size))
        self.posters.append(disk.DiskFreeOnRoot(size))
        self.posters.append(memory.FreeAndSwap(size))
        self.posters.append(cpu.CpuTemp(size))
        self.posters.append(cpu.CpuLoad(size))
        self.posters.append(disk.DiskIO(size))

    # This can be as dynamic as needed, here the static list is just
    # traversed forever
    def get_next(self):
        self.index += 1
        return self.posters[self.index % len(self.posters)]


def launch():
    try:
        _posters = Posters()
        seq = Sequenser(device, _posters.get_next, args.image_file)

        _posters.construct((args.poster_width, device.height))

        if args.yappi:
            seq.configure_slide(0, 1, 0)  # Full tilt
            start_yappi()
        else:
            seq.configure_slide(4, 1, 0.080)  # 3 secs and then a slow scroll

        seq.activate()

        if args.yappi:
            time.sleep(30)
            seq.terminate()
            stop_yappi()
        else:
            # continous scrolling
            while seq.isAlive():
                seq.join(1)

    except KeyboardInterrupt:
        seq.terminate()

    for p in _posters.posters:
        p.terminate()


launch()
