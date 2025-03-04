# Import
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
import torchvision.datasets as datasets
import torchvision.transforms as transforms

# Create FCN
class NeuralNetwork(nn.Module):
    def __init__(self, input_size, num_classes):
        super(NeuralNetwork, self).__init__() 
        self.fc1 = nn.Linear(in_features=input_size, out_features=50)
        self.fc2 = nn.Linear(in_features=50, out_features=num_classes)

    def forward(self, x):
        return self.fc2(F.relu(self.fc1(x)))

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') 
print(device)

# hyperparameters
input_size = 784
num_classes = 10
learning_rate = 0.001
batch_size = 64
num_epochs = 1

# Load data
train_data = datasets.MNIST(root="dataset/", train=True, transform=transforms.ToTensor(), download=True)
train_loader = DataLoader(dataset=train_data, batch_size=batch_size, shuffle=True)
test_data = datasets.MNIST(root="dataset/", train=False, transform=transforms.ToTensor(), download=True)
test_loader = DataLoader(dataset=test_data, batch_size=batch_size, shuffle=True)

# Initialize network
model = NeuralNetwork(input_size=input_size, num_classes=num_classes).to(device)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(params=model.parameters(), lr=learning_rate)

# Training
for epoch in range(num_epochs):
    for batch_idx, (data, labels) in enumerate(train_loader):
        data = data.to(device=device)
        labels = labels.to(device=device)

        data = data.reshape(data.shape[0], -1) 

        scores = model(data)
        loss = criterion(scores, labels)

        optimizer.zero_grad() 
        loss.backward() 

        optimizer.step() 

# Testing
num_correct = 0
num_samples = 0
model.eval() 

with torch.no_grad():
    for data, labels in test_loader:
        data = data.to(device=device)
        labels = labels.to(device=device)

        data = data.reshape(data.shape[0], -1)

        scores = model(data)

        _, predictions = torch.max(scores, dim=1)
        num_correct += (predictions == labels).sum()
        num_samples += predictions.size(0)

    print(f'Got {num_correct} / {num_samples} with accuracy {float(num_correct) / float(num_samples) * 100:.2f}')

model.train()

import matplotlib.pyplot as plt

# Test and plot 10 random images
model.eval()
with torch.no_grad():
    fig, axs = plt.subplots(3, 5, figsize=(12, 6))
    axs = axs.flatten()

    for i, (data, labels) in enumerate(test_loader):
        if i >= 15:  # Break after 15 images
            break

        data = data.to(device=device)
        labels = labels.to(device=device)

        data = data.reshape(data.shape[0], -1)

        scores = model(data)

        _, predictions = torch.max(scores, dim=1)

        # Plot the image and prediction result
        img = data.cpu().numpy().reshape(-1, 28, 28)
        axs[i].imshow(img[0], cmap='gray')
        axs[i].set_title(f"Label: {labels[0]} - Prediction: {predictions[0]}")

    plt.tight_layout()
    plt.show()

model.train()