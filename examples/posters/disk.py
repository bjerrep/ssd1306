
import time
import subprocess
from oled.sequenser import ThreadedPoster
import font


class DiskFreeOnRoot(ThreadedPoster):
    def __init__(self, size):
        super(DiskFreeOnRoot, self).__init__(size, self.get_clock)
        self.image = self.get_new_image()

    def get_clock(self):
        x = self.width / 2
        left = 5

        while not self.is_terminated():
            ret = subprocess.check_output(
                'df -h | grep " /$" | awk \'{print $3 " " $4}\'', shell=True)
            used, free = ret.split()

            image, draw = self.get_new_image_and_canvas()
            pos = font.text(draw, (x, 3),
                            'Disk', 'large', 'hcenter')
            pos = font.text(draw, (left, pos[1]),
                            'Used:', 'small')
            pos = font.text(draw, (self.width - 5, pos[1] - 3),
                            str(used), 'normal', 'right')
            pos = font.text(draw, (left, pos[1] - 5),
                            'Free:', 'small')
            pos = font.text(draw, (self.width - 5, pos[1] - 3),
                            str(free), 'normal', 'right')
            self.image = image
            self.new_image_is_ready()
            time.sleep(1)

    def get_image(self):
        return self.image
