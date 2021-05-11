#!/usr/bin/env python
# coding: utf-8

import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import string

def log_polar(arr, cy, cx, radius):
    #print(arr, cy, cx, radius)
    r_len = 5
    theta_len = 12
    r_arr = np.logspace(np.log10(1), np.log10(radius), r_len+1)
    theta_arr = np.linspace(-np.pi, np.pi, theta_len+1) # by arctan2
    def p(r, theta):
        dy = int(r_arr[r]*np.sin(theta_arr[theta]))
        dx = int(r_arr[r]*np.cos(theta_arr[theta]))
        return dy, dx
    def inside(r, theta, dy, dx):
        # whether (dx, dy) inside the area
        d_th = np.arctan2(dy, dx)
        d_r = np.sqrt(np.power(dy, 2)+np.power(dx, 2))
        #print(f"{r_arr[r]:.2f}, {r_arr[r+1]:.2f}, {theta_arr[theta]:.2f}, {theta_arr[theta+1]:.2f}, {d_r:.2f}, {d_th:.2f}, {dy}, {dx}")
        return r_arr[r] <= d_r <= r_arr[r+1] and\
            theta_arr[theta] <= d_th <= theta_arr[theta+1]
    def v(visited, y, x):
        return visited[y+radius+1, x+radius+1]
    def sv(visited, y, x, value):
        visited[y+radius+1, x+radius+1] = value
    def a(arr, y, x):
        # wrapper for exceeded access
        if 0 <= y < arr.shape[0] and 0 <= x < arr.shape[1]:
            return arr[y, x]
        else:
            return 0
    res = np.zeros((r_len, theta_len))
    for r in range(r_len):
        for theta in range(theta_len):
            #print(r, theta)
            shape = arr.shape
            visited = np.zeros((shape[0]+2*radius+2, shape[1]+2*radius+2), dtype=np.int32)
            dy, dx = p(r, theta)
            y = cy + dy
            x = cx + dx
            #print(dy, dx, y, x)
            sv(visited, y, x, 1)
            q = [(y, x)]
            c = [a(arr, y, x)]
            while q:
                y, x = q.pop(0)
                for i in [-1, 0, 1]:
                    for j in [-1, 0, 1]:
                        ny = y + j
                        nx = x + i
                        if v(visited, ny, nx) == 0 and inside(r, theta, ny-cy, nx-cx):
                            sv(visited, ny, nx, 1)
                            q.append((ny, nx))
                            c.append(a(arr, ny, nx))
            #print(visited)
            res[r, theta] = np.average(c)
    return res.reshape(-1)

def aiss(arr):
    radius = np.min(arr.shape) // 2
    y_arr = np.linspace(0, arr.shape[0]-1, 7)
    x_arr = np.linspace(0, arr.shape[1]-1, 7)
    return [[ log_polar(arr, int(y), int(x), radius) for x in x_arr ] for y in y_arr ]

def d_aiss(arr1, arr2):
    return np.array([[ np.linalg.norm(arr1[y][x]-arr2[y][x]) for x in range(len(arr1[y])) ] for y in range(len(arr1)) ]).reshape(-1).sum()

def font2img(char, img_w, img_h, font_file):
    image = Image.new('1', (img_w, img_h), 1) # default color: white
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_file, img_h)
    (font_width, font_height) = font.getsize(char)
    x = (img_w - font_width)/2
    y = (img_h - font_height)/2
    draw.text((x, y), char, 0, font=font)
    return (np.array(image.convert('L')) > 0).astype(np.uint8)

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
charset_aiss = {
    ch: aiss(im)
    for ch, im in charset_img.items()
}

def score(ch, block):
    return d_aiss(charset_aiss[ch], aiss(block))
    #return abs(charset_sdf[ch] - to_sdf(block)).astype(int).sum() # + 0.8 * abs(charset_img[ch].astype(int).sum() - block.astype(int).sum())

def best_char(block):
    return min(charset_aiss, key=lambda k: score(k, block))

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

def font2img_tweak(char, img_w, img_h, font_file):
    image = Image.new('1', (img_w, img_h), 1) # default color: white
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_file, img_h)
    (font_width, font_height) = font.getsize(char)
    x = (img_w - font_width)/2
    y = (img_h - font_height)/2
    draw.text((x, y), char, 0, font=font)
    # TODO: add tweaks and noises on the image
    m1 = (np.random.rand()-0.5)*2*0.3
    m2 = (np.random.rand()-0.5)*2*0.3
    image = image.transform(image.size, Image.AFFINE, (1, m1, 0, m2, 1, 0), Image.BICUBIC)
    return (np.array(image.convert('L')) > 0).astype(np.uint8)

#eg = np.random.rand(20)
#
#for r in eg:
#    c = charset[int(len(charset)*r)]
#    img = font2img_tweak(c, block_w, block_h, font_file)
#    t = best_char(img)
#    print(c, t)

#heat = np.zeros((len(charset), len(charset)))
#print('  ', end='')
#for x in charset:
#    print(f'{x}    ', end='')
#print('')
#for x in range(len(charset)):
#    print(f'{charset[x]} ', end='')
#    for y in range(len(charset)):
#        t = d_aiss(charset_aiss[charset[x]], charset_aiss[charset[y]])
#        heat[x, y] = t
#        print(f'{t:.2f} ', end='')
#    print('')
#import matplotlib.pyplot as plt
#plt.imshow(heat, cmap='hot', interpolation='nearest')
#plt.show()

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
            f = f.filter(ImageFilter.CONTOUR)
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
