
import time
import subprocess
from oled.sequenser import ThreadedPoster
import font


class FreeAndSwap(ThreadedPoster):
    def __init__(self, size):
        super(FreeAndSwap, self).__init__(size, self.get_clock)
        self.image = self.get_new_image()

    def get_clock(self):
        x = self.width / 2
        left = 5

        while not self.is_terminated():
            ret = subprocess.check_output(
                'free -h | xargs | awk \'{print $10 " " $16}\'', shell=True)
            mem_free, swap_used = ret.split()

            image, draw = self.get_new_image_and_canvas()
            pos = font.text(draw, (x, 3),
                            'Memory', 'large', 'hcenter')
            pos = font.text(draw, (left, pos[1]),
                            'Free:', 'small')
            pos = font.text(draw, (self.width - 5, pos[1] - 3),
                            mem_free, 'normal', 'right')
            pos = font.text(draw, (left, pos[1] - 3),
                            'Swapped:', 'small')
            pos = font.text(draw, (self.width - 5, pos[1] - 3),
                            swap_used, 'normal', 'right')
            self.image = image
            self.new_image_is_ready()
            time.sleep(1.8)

    def get_image(self):
        return self.image
