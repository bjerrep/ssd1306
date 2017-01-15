
import subprocess
import font
from oled.sequenser import ThreadedPoster
import psutil
import widgets
import time
import re

nof_cpu = psutil.cpu_count()
bottom_margin = 4


class CpuTemp(ThreadedPoster):

    def __init__(self, size):
        super(CpuTemp, self).__init__(size, self.get_cpu_load_and_redraw)

    def get_cpu_load_and_redraw(self):
        xc = self.width / 2
        yh = self.height - widgets.title_height
        yc = widgets.title_height + yh / 2
        r = self.height - bottom_margin - yc

        while not self.is_terminated():
            image, draw = self.get_new_image_and_canvas()

            font.text(draw, (self.width / 2, widgets.title_height / 2),
                      'CpuTemp', alignment='middle')

            try:
                ret = subprocess.check_output(
                    ['/opt/vc/bin/vcgencmd measure_temp'], shell=True)
                temperature = float(re.search("\d+\.\d+",
                                    ret.decode('utf8')).group(0))
                widgets.meter(draw, xc - r, yc - r, xc + r, yc + r,
                              40, 80, temperature)
            except:
                font.text(draw, (xc, yc), 'not pi ?', alignment='middle')

            self.image = image
            del image
            del draw
            self.new_image_is_ready()
            time.sleep(2)


class CpuLoad(ThreadedPoster):

    def __init__(self, size):
        super(CpuLoad, self).__init__(size, self.get_cpu_load_and_redraw)

    def get_cpu_load_and_redraw(self):
        bar_height = self.height - widgets.title_height - bottom_margin - 3
        width_cpu = self.width / nof_cpu
        bar_width = 0.5 * width_cpu
        bar_margin = (width_cpu - bar_width) / 2
        interval = 0.05

        while not self.is_terminated():
            image, draw = self.get_new_image_and_canvas()

            font.text(draw, (self.width / 2, widgets.title_height / 2),
                      'CpuLoad', alignment='middle')

            ret = subprocess.check_output(
                'LANG=C top -d%f -bn2 | grep "Cpu[0123]" | tail -n%d | '
                'awk \'{print $3}\' | cut -d/ -f1' %
                (interval, nof_cpu), shell=True)

            percentages = [float(x) for x in ret.split()]
            interval = 0.5
            x = bar_margin

            for cpu in percentages:
                y2 = self.height - bottom_margin
                widgets.vertical_bar(draw,
                                     x, y2 - bar_height - 1,
                                     x + bar_width, y2, cpu / 100.0)
                x += width_cpu

            self.image = image
            del image
            del draw
            self.new_image_is_ready()
