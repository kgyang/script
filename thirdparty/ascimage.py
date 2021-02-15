#!/bin/python3

import sys
from PIL import Image, ImageDraw, ImageFont, ImageColor
import numpy as np


def main(ifile, ofile, sc):
    img = Image.open(ifile)

    font = ImageFont.load_default()
    letter_width = font.getsize("x")[0]
    letter_height = font.getsize("x")[1]

    wcf = letter_height/letter_width

    width = round(img.size[0]*sc*wcf)
    height = round(img.size[1]*sc)

    img = img.resize((width, height))

    img = np.sum(np.asarray(img), axis=2)
    min_i = img.min()
    max_i = img.max()
    img -= min_i
    img = (1.0 - img/(max_i - min_i))

    chars = np.asarray(list(' .,:irs?@9B&#'))

    img = img*(chars.size - 1).astype(int)

    lines = ("\n".join(("".join(r) for r in chars[img]))).split("\n")

    bgcolor = 'white'
    n_width = letter_width*width
    n_height = letter_height*height
    n_img = Image.new("RGBA", (n_width, n_height), bgcolor)
    draw = ImageDraw.Draw(n_img)

    nbins = len(lines)
    color_range = list(ImageColor('black').range_to(ImageColor('blue'), nbins))

    left_padding = 0
    y = 0
    idx = 0
    for l in lines:
        color = color_range[idx]
        idx += 1
        draw.text((left_padding, y), line, color.hex, font=font)
        y += letter_height

    n_img.save(ofile)

if __name__ == '__main__':
    main(sys.args[1], sys.args[2], 1)
