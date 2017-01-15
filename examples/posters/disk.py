
import time
import subprocess
from oled.sequenser import ThreadedPoster
import font
import widgets


class DiskFreeOnRoot(ThreadedPoster):
    def __init__(self, size):
        super(DiskFreeOnRoot, self).__init__(size, self.get_clock)

    def get_clock(self):
        x = self.width / 2
        left = 5

        while not self.is_terminated():
            ret = subprocess.check_output(
                'df -h | grep " /$" | awk \'{print $3 " " $4}\'', shell=True)
            used, free = ret.decode('utf-8').split()
            image, draw = self.get_new_image_and_canvas()
            pos = font.text(draw, (x, 3),
                            'Disk', 'large', 'hcenter')
            pos = font.text(draw, (left, pos[1]),
                            'Used:', 'small')
            pos = font.text(draw, (self.width - 5, pos[1] - 3),
                            used, 'normal', 'right')
            pos = font.text(draw, (left, pos[1] - 5),
                            'Free:', 'small')
            pos = font.text(draw, (self.width - 5, pos[1] - 3),
                            free, 'normal', 'right')
            self.image = image
            self.new_image_is_ready()
            time.sleep(1)


class DiskIO(ThreadedPoster):
    def __init__(self, size):
        """displays disk i/o for a given hardcoded
           diskname on an completely arbitrary scale.
        """
        super(DiskIO, self).__init__(size, self.get_clock)
        self.disk = 'mmcblk0'

    def get_clock(self):
        x = self.width / 2
        left = 5
        bar_height = 8
        measurement_time = 1

        while not self.is_terminated():
            ret = subprocess.check_output(
                'iostat -d %i 1 -y | grep %s | awk \'{print $3 " " $4}\'' %
                (measurement_time, self.disk), shell=True)
            read, write = ret.split()

            image, draw = self.get_new_image_and_canvas()
            pos = font.text(draw, (x, 0),
                            'DiskI/O', 'large', 'hcenter')

            pos = font.text(draw, (left, pos[1]),
                            'Read', 'small')
            widgets.horizontal_bar(draw, left, pos[1],
                                   self.width - left, pos[1] + bar_height,
                                   float(read) / 100.0)
            pos = (pos[0], pos[1] + bar_height + 4)

            pos = font.text(draw, (left, pos[1]),
                            'Write', 'small')
            widgets.horizontal_bar(draw, left, pos[1],
                                   self.width - left, pos[1] + bar_height,
                                   float(write) / 100.0)

            self.image = image
            self.new_image_is_ready()
            measurement_time = 2
