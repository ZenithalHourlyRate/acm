#!/usr/bin/env python
# coding: utf-8

# In[1]:


import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy
import string


# In[2]:


def font2img(char, img_w, img_h, font_file):
    image = Image.new('1', (img_w, img_h), 1) # default color: white
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_file, img_h)
    (font_width, font_height) = font.getsize(char)
    x = (img_w - font_width)/2
    y = (img_h - font_height)/2
    draw.text((x, y), char, 0, font=font)
    return (numpy.array(image.convert('L')) > 0).astype(numpy.uint8)


# In[3]:


def norm_array(arr, orig):
    m, n = arr.min(), arr.max()
    arr -= m
    if n - m != 0:
        arr /= n - m
    if orig.sum() != 0:
        arr /= orig.sum() / orig.size
    return arr


# In[4]:


def to_sdf(arr):
    sdf_arr = cv2.distanceTransform(arr, cv2.CV_32F, 0)
    sdf_arr_neg = cv2.distanceTransform(1 - arr, cv2.CV_32F, 0)
    return norm_array(sdf_arr + sdf_arr_neg, arr)


# In[5]:


def sdf_print(sdf_arr):
    return Image.fromarray((sdf_arr * 255).astype(numpy.uint8), 'L')


# In[6]:


with Image.open('ba1000.png', 'r') as f:
    sample_image = numpy.array(f)
sample_image = (sample_image[:,:] > 128).astype(numpy.uint8)


# In[7]:


print(sample_image.shape)


# In[22]:


block_w = 20
block_h = 40


# In[23]:


charset = ' .-*+=#/~[]^|":'


# In[24]:


charset_img = {
    ch: font2img(ch, block_w, block_h, 'mono.otf')
    for ch in charset
}

charset_sdf = {
    ch: to_sdf(im)
    for ch, im in charset_img.items()
}


# In[58]:


def score(ch, block):
    return abs(charset_sdf[ch] - to_sdf(block)).astype(int).sum() # + 0.8 * abs(charset_img[ch].astype(int).sum() - block.astype(int).sum())


# In[59]:


def best_char(sdf):
    return min(charset_sdf, key=lambda k: score(k, sdf))


# In[60]:


def gen_art(img):
    gen = lambda x, y: best_char(img[x : x + block_h, y : y + block_w])

    return [
        [ gen(x, y) for y in range(0, img.shape[1], block_w) ]
        for x in range(0, img.shape[0], block_h)
    ]


# In[61]:


for row in gen_art(sample_image):
    for col in row:
        print(col, end='')
    print('')


# In[ ]:





# In[ ]:




