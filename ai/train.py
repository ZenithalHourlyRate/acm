import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.autograd import Variable

from font import FontDataset

from constants import *

dataset = FontDataset(charset, dataset_size, image_size, font_file)

train_loader = torch.utils.data.DataLoader(dataset=dataset,
                                           batch_size=batch_size,
                                           shuffle=True)
from lenet import Net

device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = Net(image_size, len(charset)).to(device)
loss_func=torch.nn.CrossEntropyLoss().to(device)
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.5)

def train(epoch):
    for batch_idx, (data, target) in enumerate(train_loader):
        # data.size():[64, 1, 32, 32]
        # target.size():[64]
        data, target = data.to(device), target.to(device)
        output = model(data)
        #output:64*10


        loss = loss_func(output,target)

        if batch_idx * batch_size % (dataset_size // 2) == 0:
            train_loss = 0
            correct = 0
            for data, target in train_loader:
                with torch.no_grad():
                    data, target = data.to(device), target.to(device)
                    data, target = Variable(data), Variable(target)
                    #data, target = Variable(data, volatile=True), Variable(target)
                    output = model(data)
                    # sum up batch loss
                    train_loss += loss_func(output, target).data
                    # get the index of the max log-probability
                    pred = output.data.max(1, keepdim=True)[1]
                    #print(pred)
                    correct += pred.eq(target.data.view_as(pred)).sum()
            train_loss /= len(train_loader.dataset)
            #plt_train_loss.append(train_loss)
            #plt_train_acc.append(correct/len(train_loader.dataset))
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tAverage loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader),
                train_loss, correct, len(train_loader.dataset),
                100. * correct / len(train_loader.dataset)))
            #print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
            #    epoch, batch_idx * len(data), len(train_loader.dataset),
            #    100. * batch_idx / len(train_loader), loss.data))

        optimizer.zero_grad()   
        loss.backward()         
        optimizer.step()        

for epoch in range(1, 20):
    train(epoch)

torch.save(model.state_dict(),'./model.pth')
