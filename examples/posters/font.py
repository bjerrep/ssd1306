
from PIL import ImageFont

# Make a set of standard fonts available
# FreePixel.ttf from http://www.dafont.com/bitmap.php
ttf = 'fonts/FreePixel.ttf'
fontsizes = {'huge': 26, 'large': 15, 'normal': 13, 'small': 10}

# fonts dictionary: {name: (font, height), ... }
fonts = {k: (ImageFont.truetype(ttf, v),
             ImageFont.truetype(ttf, v).getsize('bg')[1])
         for k, v in fontsizes.items()}


def text(canvas, pos, text, size='normal',
         alignment=None, color='white'):

    font, height = fonts[size]

    if alignment == 'middle':
        pos = (pos[0] - font.getsize(text)[0] / 2, pos[1] - height / 2)
    elif alignment == 'vcenter':
        pos = (pos[0], pos[1] - height / 2)
    elif alignment == 'hcenter':
        pos = (pos[0] - font.getsize(text)[0] / 2, pos[1])
    elif alignment == 'low':
        pos = (pos[0], pos[1] - height)
    elif alignment == 'right':
        pos = (pos[0] - font.getsize(text)[0], pos[1])

    canvas.text(pos, text, color, font=font)
    return (pos[0], pos[1] + int(height * 1.2))


def font_height(size_name):
    return fonts[size_name][1]


def text_width(size_name, text):
    return fonts[size_name][0].getsize(text)[0]
