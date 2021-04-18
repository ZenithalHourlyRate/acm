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

def sdf_print(sdf_arr):
    return Image.fromarray((sdf_arr * 255).astype(numpy.uint8), 'L')

block_w = 20
block_h = 40
block_w_num = 36
block_h_num = 13
font_file = 'mono.otf'
charset = ' .-*+=#/~[]^|":'
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

def gen_art(img):
    gen = lambda x, y: best_char(img[x : x + block_h, y : y + block_w])

    return [
        [ gen(x, y) for y in range(0, img.shape[1], block_w) ]
        for x in range(0, img.shape[0], block_h)
    ]

def img2ascii(num):
    with Image.open(f'img/ba_{num:04d}.png', 'r') as f:
        f = f.convert("L")
        f = f.resize((block_w*block_w_num, block_h*block_h_num))
        img = numpy.array(f)
    img = (img[:,:] > 128).astype(numpy.uint8)

    font = ImageFont.truetype(font_file, block_h)
    out = Image.new('1', (block_w*block_w_num, block_h*block_h_num), 1) # default color: white
    draw = ImageDraw.Draw(out)

    for j, row in enumerate(gen_art(img)):
        for i, col in enumerate(row):
            (font_width, font_height) = font.getsize(col)
            x = (block_w - font_width)/2
            y = (block_h - font_height)/2
            draw.text((i*block_w+x, j*block_h+y), col, 0, font=font) # font color: black
            #draw.rectangle([(i*block_w, j*block_h), ((i+1)*block_w, (j+1)*block_h)], outline=0) # font color: black
            #print(col, end='')
        #print('')

    out.save(f'output/ba_{num:04d}.png')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='i,g2ascii impl by dram')
    parser.add_argument('-j', dest='jobs', type=int, help='total num of jobs')
    parser.add_argument('-n', dest='job', type=int, help='the num of job for this program')
    args = parser.parse_args()

    total_frame = 6574
    for num in range(1, total_frame+1):
        if args.job != None and args.jobs != None and num % args.jobs != args.job:
            continue
        img2ascii(num)
        print(f'{num} finished')
