
import socket
import fcntl
import struct
import time

from oled.sequenser import ThreadedPoster
import font


class Summary(ThreadedPoster):
    def __init__(self, size):
        super(Summary, self).__init__(size, self.refresh)
        self.image = self.get_new_image()

    def refresh(self):
        x = self.width / 2
        left = 5
        while not self.is_terminated():
            try:
                eth = self.get_ip_address('eth0')
            except:
                eth = 'none'
            try:
                wifi = self.get_ip_address('wlan0')
            except:
                wifi = 'none'

            image, draw = self.get_new_image_and_canvas()
            pos = font.text(draw, (x, 3),
                            'Net', 'large', 'hcenter')
            pos = font.text(draw, (left, pos[1] - 2),
                            'eth0:', 'small')
            pos = font.text(draw, (x, pos[1] - 3),
                            str(eth), 'small', 'hcenter')
            pos = font.text(draw, (left, pos[1] - 2),
                            'wlan0:', 'small')
            pos = font.text(draw, (x, pos[1] - 3),
                            str(wifi), 'small', 'hcenter')
            self.image = image
            self.new_image_is_ready()
            time.sleep(2)

    def get_ip_address(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ifaddr = fcntl.ioctl(s.fileno(), 0x8915,
                             struct.pack('256s', ifname[:15]))[20:24]
        return socket.inet_ntoa(ifaddr)

    def get_image(self):
        return self.image
