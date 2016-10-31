#!/usr/bin/env python

import sys
import time
from oled.sequenser import Sequenser

sys.path.append('posters')
import clock
import cpu
import disk
import net
import memory

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


w = 128
h = 64
size = (w, h)
half = (w / 2, h)

posters = []
posters.append(net.Summary(half))
posters.append(disk.DiskFreeOnRoot(half))
posters.append(clock.Clock(half))
posters.append(memory.FreeAndSwap(half))
posters.append(cpu.CpuTemp(half))
posters.append(cpu.CpuLoad(half))

# This can be as dynamic as needed, here the static list is just
# traversed forever

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

        seq.set_timing(4, 1, 0.080)  # 3 secs and then a slow scroll
        # seq.set_timing(0, 1, 0.040)  # continous scrolling
        while seq.isAlive():
            seq.join(1)

    except KeyboardInterrupt:
        seq.terminate()

    for p in posters:
        p.terminate()


def launch_with_yappi():
    import yappi
    try:
        seq = Sequenser(size, get_next)

        start_yappi()
        seq.set_timing(0, 1, 0.040)
        time.sleep(60)
        seq.terminate()
        stop_yappi()

    except KeyboardInterrupt:
        seq.terminate()

    for p in posters:
        p.terminate()

yappi_profiling = False

if yappi_profiling:
    launch_with_yappi()
else:
    launch()
