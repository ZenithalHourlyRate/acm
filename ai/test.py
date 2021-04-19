import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.autograd import Variable

from font import FontDataset

from constants import *
dataset_size = 200
batch_size = 16
from lenet import Net

device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = Net(image_size, len(charset)).to(device)
model.load_state_dict(torch.load('./model.pth'))

def evaluate(image):
    image = image.to(device)
    output = model(image)
    return [charset[i.argmax()] for i in output]

if __name__ == '__main__':
    dataset = FontDataset(charset, dataset_size, image_size, font_file)
    test_loader = torch.utils.data.DataLoader(dataset=dataset,
                                               batch_size=batch_size,
                                               shuffle=True)
    for batch_idx, (data, target) in enumerate(test_loader):
        data, target = data.to(device), target.to(device)
        output = model(data)
        print([charset[i] for i in target])
        print([charset[i.argmax()] for i in output])
        break
