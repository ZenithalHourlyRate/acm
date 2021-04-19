#!/usr/bin/env python
# coding: utf-8

import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy
import string

def font2img(char, img_w, img_h, font_file):
    image = Image.new('1', (img_w, img_h), 1) # default color: white
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_file, img_h)
    (font_width, font_height) = font.getsize(char)
    x = (img_w - font_width)/2
    y = (img_h - font_height)/2
    draw.text((x, y), char, 0, font=font)
    return (numpy.array(image.convert('L')) > 0).astype(numpy.uint8)

def norm_array(arr, orig):
    m, n = arr.min(), arr.max()
    arr -= m
    if n - m != 0:
        arr /= n - m
    if orig.sum() != 0:
        arr /= orig.sum() / orig.size
    return arr

def to_sdf(arr):
    sdf_arr = cv2.distanceTransform(arr, cv2.CV_32F, 0)
    sdf_arr_neg = cv2.distanceTransform(1 - arr, cv2.CV_32F, 0)
    return norm_array(sdf_arr + sdf_arr_neg, arr)

block_w = 20
block_h = 40
block_w_num = 64
block_h_num = 18
font_file = 'mono.otf'
charset = ' .\'`^_-~:+/\\|[]#'
charset_img = {
    ch: font2img(ch, block_w, block_h, font_file)
    for ch in charset
}
charset_sdf = {
    ch: to_sdf(im)
    for ch, im in charset_img.items()
}

def score(ch, block):
    return abs(charset_sdf[ch] - to_sdf(block)).astype(int).sum() # + 0.8 * abs(charset_img[ch].astype(int).sum() - block.astype(int).sum())

def best_char(sdf):
    return min(charset_sdf, key=lambda k: score(k, sdf))

def img2acm(img):
    gen = lambda x, y: best_char(img[x : x + block_h, y : y + block_w])

    # this is called acm
    return [
        [ gen(x, y) for y in range(0, img.shape[1], block_w) ]
        for x in range(0, img.shape[0], block_h)
    ]

def acm2img(acm):
    font = ImageFont.truetype(font_file, block_h)
    out = Image.new('1', (block_w*block_w_num, block_h*block_h_num), 1) # default color: white
    draw = ImageDraw.Draw(out)

    for j, row in enumerate(acm):
        for i, col in enumerate(row):
            (font_width, font_height) = font.getsize(col)
            x = (block_w - font_width)/2
            y = (block_h - font_height)/2
            draw.text((i*block_w+x, j*block_h+y), col, 0, font=font) # font color: black

            # for DEBUG
            #draw.rectangle([(i*block_w, j*block_h), ((i+1)*block_w, (j+1)*block_h)], outline=0) # font color: black

    return out


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Convert video to ')
    parser.add_argument('-j', dest='jobs', type=int, help='total num of jobs', required=True)
    parser.add_argument('-n', dest='job', type=int, help='the num of job for this program (start from 1)', required=True)
    parser.add_argument('-i', dest='input', type=str, help='input imgs', required=True)
    parser.add_argument('-o', dest='output', type=str, help='output files', required=True)
    parser.add_argument('-s', dest='size', type=str, help='size', default='40x12')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', action='store_true', help='output Ascii Movie in txt format')
    group.add_argument('-g', action='store_true', help='output Ascii Movie in image format')
    args = parser.parse_args()

    if args.size:
        # change global state
        block_w_num, block_h_num = args.size.split('x')
        block_w_num, block_h_num = int(block_w_num), int(block_h_num)

    count = 1 # assumption made by ffmpeg
    from os.path import isfile
    while isfile(args.input.format(count)):
        input_file = args.input.format(count)
        output_file = args.output.format(count)

        if count % args.jobs + 1 != args.job:
            count += 1
            continue

        with Image.open(input_file, 'r') as f:
            f = f.convert("L")
            f = f.resize((block_w*block_w_num, block_h*block_h_num))
            img = numpy.array(f)
        img = (img[:,:] > 128).astype(numpy.uint8) # L to 1

        acm = img2acm(img)
        if args.a:
            with open(output_file, 'w') as f:
                for j, row in enumerate(acm):
                    for i, col in enumerate(row):
                        print(col, file=f, end='')
                    print('', file=f) # newline
        else:
            img = acm2img(acm)
            img.save(output_file)
        print(f'{count} finished')
        count += 1
