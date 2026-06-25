"""
CNN模型 - 圆形vs方形二分类
28x28灰度图, 2分类
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class SimpleCNN(nn.Module):
    """轻量级CNN, 28x28灰度图 -> 2分类"""
    def __init__(self, num_classes=2):
        super(SimpleCNN, self).__init__()

        # Block1: 1->16, 28->14
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(16)

        # Block2: 16->32, 14->7
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(32)

        # Block3: 32->64, 7->3 (padding=0 so 7->5, then pool to 2)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=0)
        self.bn3 = nn.BatchNorm2d(64)

        # 全连接
        self.dropout = nn.Dropout(0.4)
        self.fc1 = nn.Linear(64 * 2 * 2, 128)
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = F.max_pool2d(F.relu(self.bn1(self.conv1(x))), 2)  # 28->14
        x = F.max_pool2d(F.relu(self.bn2(self.conv2(x))), 2)  # 14->7
        x = F.max_pool2d(F.relu(self.bn3(self.conv3(x))), 2)  # 5->2 (kernel=3, pad=0: 7-2=5)

        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(self.dropout(x)))
        x = self.fc2(x)
        return x


if __name__ == '__main__':
    model = SimpleCNN(num_classes=2)
    x = torch.randn(4, 1, 28, 28)
    out = model(x)
    print(f"输入: {x.shape} -> 输出: {out.shape}")
    print(f"参数量: {sum(p.numel() for p in model.parameters()):,}")
