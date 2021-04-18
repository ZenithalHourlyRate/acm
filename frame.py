from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from torchvision import transforms
import torch

from test import evaluate
from constants import *

def img2ascii(num):
    im = Image.open(f'img/ba_{num:04d}.png')
    im = im.convert("L")
    im = im.filter(ImageFilter.CONTOUR)
    im = im.convert("1")
    
    w, h = im.size
    image_size = 16
    X, Y = w//image_size, h//image_size
    
    image = Image.new('1', (image_size*X, image_size*Y), 1) # default color: white
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('mono.otf', image_size)
    
    for i in range(X):
        t = None
        for j in range(Y):
            sub = im.crop((i*image_size, j*image_size, (i+1)*image_size, (j+1)*image_size))
            sub = sub.resize((32, 32), Image.ANTIALIAS)
            toTensor = transforms.Compose([\
                    transforms.ToTensor()])
            sub = toTensor(sub)
            sub = sub.unsqueeze(0) # add batch dimension
            t = sub if t == None else torch.cat((t, sub), 0)

        chars = evaluate(t)

        for j in range(Y):
            char = chars[j]
            (font_width, font_height) = font.getsize(char)
            x = (image_size - font_width)/2
            y = (image_size - font_height)/2
            draw.text((i*image_size+x, j*image_size+y), char, 0, font=font) # font color: black
            #draw.rectangle([(i*image_size, j*image_size), ((i+1)*image_size, (j+1)*image_size)], outline=0) # font color: black
    
    image.save(f'output/ba_{num:04d}.png')

for num in range(1, 6574+1):
    img2ascii(num)
    print(f'{num} finished')
