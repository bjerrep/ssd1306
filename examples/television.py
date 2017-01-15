
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init(None)

from PIL import Image
from demo_opts import device
import argparse
import sys
import time

# these will not show up in help
parser = argparse.ArgumentParser()
parser.add_argument('--url', type=str, help='Http live stream')
parser.add_argument('--video', type=str, help='Videofile (any format)')
parser.add_argument('--test', type=int,
                    default=-1, help='Gstreamer videotestsrc pattern (try 18)')
args, unknown = parser.parse_known_args()


if args.video:
    source = 'filesrc location="%s" ! decodebin ! ' % args.video
elif args.test != -1:
    source = 'videotestsrc pattern=%s ! ' % args.test
else:
    if not args.url:
        args.url = """http://dr01-lh.akamaihd.net/i/dr01_0@147054/
index_5_av-b.m3u8?sd=10&b=1400-4000&rebase=on"""
    source = 'souphttpsrc location="%s" ! decodebin ! ' % args.url

pipeline = Gst.parse_launch(
    source +
    'videoscale ! video/x-raw,width=%i,height=%i ! ' % device.size +
    'videoconvert ! video/x-raw,format=GRAY8 ! ' +
    'appsink sync=true drop=true name=appsink emit-signals=true')


image = Image.new(device.mode, device.size)
threshold = 0x80

appsink = pipeline.get_by_name('appsink')
pipeline.set_state(Gst.State.PLAYING)

fps = 0
fps_time = time.time() + 1
gstreamer_running = False

while True:
    sample = appsink.emit('pull-sample')
    buf = sample.get_buffer()
    data_size = buf.get_size()
    data = bytearray(buf.extract_dup(0, data_size))

    fps += 1
    if fps_time < time.time():
        fps_time += 1
        if gstreamer_running:
            print(' fps %i' % fps)
        fps = 0
        gstreamer_running = True

    if args.video or args.url:
        threshold = 0
        for t in range(0, data_size, data_size // 100):
            threshold += int(data[t])
        threshold //= 100
        sys.stderr.write('\rthreshold %i  ' % threshold)

    image = bytearray(data_size // 8)

    for i in range(0, data_size, 8):
        image[i // 8] = ((data[i + 0] > threshold) and 0x80) | \
                        ((data[i + 1] > threshold) and 0x40) | \
                        ((data[i + 2] > threshold) and 0x20) | \
                        ((data[i + 3] > threshold) and 0x10) | \
                        ((data[i + 4] > threshold) and 0x08) | \
                        ((data[i + 5] > threshold) and 0x04) | \
                        ((data[i + 6] > threshold) and 0x02) | \
                        ((data[i + 7] > threshold) and 0x01)

    image = Image.frombytes("1", device.size, bytes(image))
    device.display(image)
