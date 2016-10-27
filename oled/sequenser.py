# The MIT License (MIT)
#
# Copyright (c) 2015 Richard Hull
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# The Sequenser walks through a list of Posters defined by the client.
# The intention is to make the life easier for client applications which
# now just need to make the individual posters and don't need to bother with
# the timeline.
# See poster_demo.py for an client example.

from PIL import Image, ImageDraw, ImageFont

try:
    import oled.device
    import oled.render
    serial_interface = oled.device.SPI(
                            port=0, spi_bus_speed_hz=32000000,
                            gpio_command_data_select=24, gpio_reset=25)
    device = oled.device.sh1106(serial_interface)
except:
    print('ssd1306 interface not available')

import threading
import time

# Make a set of standard fonts available
# DriodSans come from the package ttf_droid on Arch
ttf = 'DroidSans.ttf'
fontsizes = {'huge': 20, 'large': 14, 'normal': 9, 'small': 7}

# fonts dictionary: {name: (font, height), ... }
fonts = {k: (ImageFont.truetype(ttf, v),
             ImageFont.truetype(ttf, v).getsize('bg')[1])
         for k, v in fontsizes.items()}


# The Poster base class. Can be used for responsive and/or static posters.
#
class Poster(object):
    def __init__(self, size):
        self.width, self.height = size

    def size(self):
        return self.width, self.height

    def get_new_image(self):
        return Image.new('1', self.size())

    def get_new_image_and_canvas(self):
        image = self.get_new_image()
        return image, ImageDraw.Draw(image)

    def _activate(self):
        pass

    def _deactivate(self):
        pass

    def terminate(self):
        pass

    def set_redraw_lock(self, lock):
        pass

    def text(self, canvas, pos, text, size='normal',
             alignment=None, color='white'):

        font, height = fonts[size]

        if alignment == 'middle':
            pos = (pos[0] - font.getsize(text)[0] / 2, pos[1] - height / 2)
        elif alignment == 'vcenter':
            pos = (pos[0], pos[1] - height / 2)
        elif alignment == 'hcenter':
            pos = (pos[0] - font.getsize(text)[0] / 2, pos[1])

        canvas.text(pos, text, color, font=font)
        return (pos[0], pos[1] + int(height*1.2))


# A threaded Poster version. Used when the Poster uses long running calls
# which can then be stuffed away in a thread. This thread will then have to
# make asynchoneous callbacks for redrawing via new_image_is_ready()
#
class ThreadedPoster(Poster):
    def __init__(self, size, run_method):
        super(ThreadedPoster, self).__init__(size)
        self.terminated = False
        self.run_method = run_method

    # Dependency flip
    #
    def set_redraw_lock(self, lock):
        self.redraw_lock = lock

    def terminate(self):
        self.terminated = True

    # The poster thread must sample this and leave when
    # is_terminated() returns True
    #
    def is_terminated(self):
        return self.terminated

    def _activate(self):
        self.terminated = False
        self.thread = threading.Thread(target=self.run_method)
        self.thread.start()

    def _deactivate(self):
        self.terminated = True

    def new_image_is_ready(self):
        self.redraw_lock.release()


# The central Sequenser. Retrieves new Posters as they are needed and
# manages sliding between posters.
# The Sequenser starts when constructed and runs by itself. It will
# call a user supplied method in order to get the posters to display.
# The only public methods are terminate() and set_timing()
#
class Sequenser(threading.Thread):

    def __init__(self, size, get_next_poster, destination_file=None):
        threading.Thread.__init__(self)
        self.size = size
        self.get_next_poster = get_next_poster
        self.destination_file = destination_file
        self.terminated = False

        self.redraw_lock = threading.Semaphore()
        self.offset_redraw_lock = threading.Lock()

        self.index = -1
        self.offset = 0
        self.active_posters = []

        self.poster_display_time = 7
        self.pixel_step = 1
        self.sleep_per_step = 0.03

        self.start()
        threading.Thread(target=self._slide_event_thread).start()

    def terminate(self):
        self.redraw_lock.release()
        self.terminated = True

    # Set the pixel_step equal to the width of the display to disable
    # scrolling. Its easy to get hit by performance bottlenecks when
    # persuing 'the perfect scroll' on a r-pi.
    #
    def set_timing(self, display_time, pixel_step, sleep_per_step):
        self.poster_display_time = display_time
        self.pixel_step = pixel_step
        self.sleep_per_step = sleep_per_step

    # Nothing smart going on here yet, just reassemble the image to show.
    # This is a cpu eater.
    #
    def _redraw(self):
        image = Image.new('1', self.size)

        of = 0
        for p in self.active_posters:
            ima = p.get_image()
            image.paste(ima, (-self.offset + of, 0))
            of += p.width

        assert(-self.offset + of >= self.size[0])
        return image

    def _refresh_poster_list(self):
        if self.active_posters and self.offset >= self.active_posters[0].width:
            self.offset = 0
            # print('removed ' + self.active_posters[0].__class__.__name__)
            self.active_posters[0]._deactivate()
            del self.active_posters[0]

        sum_w = -self.offset
        for p in self.active_posters:
            sum_w += p.width

        while sum_w < self.size[0]:
            next = self.get_next_poster()
            next.set_redraw_lock(self.redraw_lock)
            self.active_posters.append(next)
            next._activate()
            sum_w += next.width
            # print('added ' + next.__class__.__name__)

    def _slide_event_thread(self):
        while not self.terminated:
            # be responsive to e.g. a terminate from a ctrl-c
            # keyboard interrupt
            sleep_total = 0.0
            while (sleep_total < self.poster_display_time and
                   not self.terminated):
                sleep_total += 0.1
                time.sleep(0.1)

            pixels = self.active_posters[0].width
            target = time.time()
            catch_up = 0

            while pixels > 0 and not self.terminated:
                target += self.sleep_per_step
                catch_up = target - time.time()
                if catch_up > 0.0:
                    time.sleep(catch_up)
                else:
                    time.sleep(0.001)
                pixels -= self.pixel_step
                step = self.pixel_step
                if pixels < 0:
                    step -= pixels
                with self.offset_redraw_lock:
                    self.offset += step
                    self.redraw_lock.release()
             # if catch_up < -self.sleep_per_step:
             #     print("missing %.3f" % catch_up)

    def run(self):
        prev_offset = -1
        while not self.terminated:
            self.redraw_lock.acquire()
            with self.offset_redraw_lock:
                if self.offset != prev_offset:
                    prev_offset = self.offset
                    self._refresh_poster_list()
                image = self._redraw()
                if self.destination_file:
                    image.save(self.destination_file)
                else:
                    device.display_v2(image)
                time.sleep(0.001)
