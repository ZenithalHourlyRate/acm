from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps


from constants import *

im = Image.open('src.png')
im = im.convert("L")
#im = im.filter(ImageFilter.FIND_EDGES)
im = im.filter(ImageFilter.CONTOUR)
im = im.convert("1")
im.show()

w, h = im.size
X, Y = w//32, h//32

image = im #Image.new('1', (32*X, 32*Y), 1) # default color: white
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('mono.otf', image_size)

from test import evaluate

for i in range(X):
    for j in range(Y):
        sub = im.crop((i*32, j*32, (i+1)*32, (j+1)*32))
        char = evaluate(sub)
        (font_width, font_height) = font.getsize(char)
        x = (image_size - font_width)/2
        y = (image_size - font_height)/2
        draw.text((i*32+x, j*32+y), char, 0, font=font) # font color: black
        draw.rectangle([(i*32, j*32), ((i+1)*32, (j+1)*32)], outline=0) # font color: black

image.save('sample.png')
