# 搭建孪生网络进行白肺图像分类
import torch
import torch.nn as nn
import torchvision
import torchvision.models as models
import torchvision.transforms as transforms
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from PIL import Image
import os


# 定义孪生网络结构
class SiameseNetwork(nn.Module):
    def __init__(self, base_model):
        super(SiameseNetwork, self).__init__()
        self.base_model = base_model

    def forward_one(self, x):
        return self.base_model(x)

    def forward(self, input1, input2):
        output1 = self.forward_one(input1)
        output2 = self.forward_one(input2)
        return output1, output2


# 定义自定义数据集
class CustomDataset(Dataset):
    def __init__(self, image_folder, labels, transform=None):
        self.image_folder = image_folder
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index):
        img_path = os.path.join(self.image_folder, f"{index}.png")
        img = Image.open(img_path).convert("RGB")

        if self.transform:
            img = self.transform(img)

        label = self.labels[index]
        return img, label


# 设置参数
batch_size = 16
learning_rate = 0.001
num_epochs = 10

# 加载ResNet18模型
base_model = models.resnet18(pretrained=True)
num_features = base_model.fc.in_features
base_model.fc = nn.Linear(num_features, 256)  # 更改全连接层的输出维度

# 创建孪生网络
siamese_net = SiameseNetwork(base_model)

# 定义损失函数和优化器
criterion = nn.BCEWithLogitsLoss()
optimizer = optim.Adam(siamese_net.parameters(), lr=learning_rate)

# 加载数据并进行预处理
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])



# 划分训练集和验证集
train_dataset=torchvision.datasets.ImageFolder('./chest_xray/train/',transform=transform)
test_set=torchvision.datasets.ImageFolder('./chest_xray/test/',transform=transform)
val_dataset=torchvision.datasets.ImageFolder('./chest_xray/val/',transform=transform)


train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size)

# 训练模型
for epoch in range(num_epochs):
    siamese_net.train()
    for batch_idx, (inputs1, inputs2, targets) in enumerate(train_loader):
        optimizer.zero_grad()

        outputs1, outputs2 = siamese_net(inputs1, inputs2)
        loss = criterion(outputs1, outputs2, targets.float())

        loss.backward()
        optimizer.step()

        if batch_idx % 10 == 0:
            print(f"Epoch [{epoch + 1}/{num_epochs}], Batch [{batch_idx}/{len(train_loader)}], Loss: {loss.item()}")

    # 在验证集上进行评估
    siamese_net.eval()
    with torch.no_grad():
        total_correct = 0
        total_samples = 0
        for val_inputs1, val_inputs2, val_targets in val_loader:
            val_outputs1, val_outputs2 = siamese_net(val_inputs1, val_inputs2)
            val_predictions = (val_outputs1 - val_outputs2).abs().sum(dim=1) < 0.5  # 根据输出差值进行二分类判断
            total_correct += (val_predictions == val_targets.byte()).sum().item()
            total_samples += val_targets.size(0)

        val_accuracy = total_correct / total_samples
        print(f"Validation Accuracy: {val_accuracy}")

print("Training finished.")
