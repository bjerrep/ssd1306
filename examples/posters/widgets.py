
import math
import font


title_height = font.font_height('small') + 4


def vertical_bar(draw, x1, y1, x2, y2, value):
    if value < 0:
        value = 0
    elif value > 1:
        value = 1
    endp = y2 - (y2 - y1) * value
    draw.rectangle((x1, y1) + (x2, y2), 'black', 'white')
    draw.rectangle((x1, endp) + (x2, y2), 'white', 'white')


def horizontal_bar(draw, x1, y1, x2, y2, value):
    if value < 0:
        value = 0
    elif value > 1:
        value = 1
    endp = x1 + (x2 - x1) * value
    draw.rectangle((x1, y1) + (x2, y2), 'black', 'white')
    draw.rectangle((x1, y1) + (endp, y2), 'white', 'white')


def meter(draw, x1, y1, x2, y2, min, max, value):
    rx = (x2 - x1) / 2
    ry = (y2 - y1) / 2
    xc = x1 + rx
    yc = y1 + ry
    draw.ellipse([x1, y1, x2, y2], 'black', 'white')
    draw.ellipse([xc - 2, yc - 2, xc + 2, yc + 2], 'white', 'white')

    def point(val, offset=0):
        deflection = float(val - min) / (max - min)
        rad = (math.pi * 3) / 4 + (math.pi * deflection * 6) / 4
        return (xc + math.cos(rad) * (rx + offset),
                yc + math.sin(rad) * (ry + offset))

    x, y = point(min)
    x -= 12
    font.text(draw, (x, y), str(min), 'small')

    x, y = point(max)
    x += 5
    font.text(draw, (x, y), str(max), 'small')

    range = max - min
    second = int(min + range / 3)
    third = int(min + 2 * range / 3)

    x, y = point(second)
    x -= 12
    font.text(draw, (x, y), str(second), 'small', alignment='low')

    x, y = point(third)
    x += 5
    font.text(draw, (x, y), str(third), 'small', alignment='low')

    if value > max:
        value = max + range / 50
    elif value < min:
        value = min - range / 50
    draw.line([xc, yc, point(value, -4)], 'white')
