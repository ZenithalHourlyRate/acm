from PIL import Image, ImageDraw, ImageFont
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

def font2img(char, image_size, font_file):
    image = Image.new('1', (image_size, image_size), 1) # default color: white
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_file, image_size)
    (font_width, font_height) = font.getsize(char)
    x = (image_size - font_width)/2
    y = (image_size - font_height)/2
    draw.text((x, y), char, 0, font=font) # font color: black
    #image.save('sample.png')
    # TODO: add tweaks and noises on the image
    return image

class FontDataset(Dataset):
    def __init__(self, charset, length, image_size, font_file):
        self.len = length
        self.data = []
        self.label = []
        toTensor = transforms.Compose([\
                transforms.ToTensor()])
        for i in range(length):
            j = i % len(charset)
            self.data.append(\
                    toTensor(\
                    font2img(charset[j], image_size, font_file)))
            self.label.append(j)

    def __getitem__(self, idx):
        return self.data[idx], self.label[idx]

    def __len__(self):
        return self.len
