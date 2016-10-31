
import time
from oled.sequenser import ThreadedPoster
import font


class Clock(ThreadedPoster):
    def __init__(self, size):
        super(Clock, self).__init__(size, self.get_clock)
        self.image = self.get_new_image()

    def get_clock(self):
        x = self.width / 2
        last_secs = 0
        ymd_divisors = [60 * 60 * 24 * 30 * 12, 60 * 60 * 24 * 30, 60 * 60 * 24]
        hms_divisors = [60 * 60, 60, 1]

        while not self.is_terminated():
            if int(time.time()) != last_secs:
                last_secs = int(time.time())

                now = time.strftime('%H:%M:%S', time.gmtime())

                with open('/proc/uptime', 'r') as f:
                    uptime = int(f.readline().split(".")[0])

                ymd = ''
                for d in ymd_divisors:
                    f = int(uptime / d)
                    uptime -= d * f
                    ymd += '%02d:' % f
                ymd = ymd[:-1]

                hms = ''
                for d in hms_divisors:
                    f = int(uptime / d)
                    uptime -= d * f
                    hms += '%02d:' % f
                hms = hms[:-1]

                image, draw = self.get_new_image_and_canvas()
                pos = font.text(draw, (x, 3), now, 'large', 'hcenter')
                pos = font.text(draw, (x, pos[1]), 'UPTIME', 'small', 'hcenter')
                pos = font.text(draw, (x, pos[1]), ymd, 'normal', 'hcenter')
                pos = font.text(draw, (x, pos[1]), hms, 'normal', 'hcenter')
                self.image = image
                self.new_image_is_ready()

            time.sleep(0.1)

    def get_image(self):
        return self.image
