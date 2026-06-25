"""
单张图片预测 + 随机生成测试
用法:
    python predict.py                        # 随机生成10个图形预测
    python predict.py --image 图片.png       # 预测指定图片
    python predict.py --interactive          # 交互模式，逐个显示预测
"""

import argparse
import torch
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from torchvision import transforms

from model import SimpleCNN
from utils import generate_shape_dataset


def predict_tensor(model, img_tensor, device):
    """对单个tensor预测"""
    model.eval()
    with torch.no_grad():
        output = model(img_tensor.unsqueeze(0).to(device))
        probs = torch.softmax(output, dim=1).squeeze()
        pred = torch.argmax(output).item()
    return pred, probs.cpu().numpy()


def predict_random_samples(model_path='results/best_model.pth', num=10):
    """随机生成图形并预测"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    model = SimpleCNN(num_classes=2)
    state = torch.load(model_path, weights_only=True)
    model.load_state_dict(state)
    model.to(device)

    # 生成测试数据
    images, labels = generate_shape_dataset(n_samples=num, img_size=28,
                                            noise_level=0.05, seed=None)

    class_names = ['圆形', '方形']
    correct = 0

    fig, axes = plt.subplots(2, 5, figsize=(12, 5))
    axes = axes.flatten()

    for i in range(num):
        img = torch.tensor(images[i], dtype=torch.float32).unsqueeze(0)
        pred, probs = predict_tensor(model, img, device)
        true = labels[i]

        is_correct = (pred == true)
        if is_correct:
            correct += 1

        color = 'green' if is_correct else 'red'
        axes[i].imshow(images[i], cmap='gray')
        axes[i].set_title(f'真:{class_names[true]} 预:{class_names[pred]}\n'
                          f'圆:{probs[0]*100:.0f}% 方:{probs[1]*100:.0f}%',
                          color=color, fontsize=8)
        axes[i].axis('off')

    plt.tight_layout()
    plt.savefig('results/test_predictions.png', dpi=150, bbox_inches='tight')
    print(f"\n准确率: {correct}/{num} ({100*correct/num:.1f}%)")
    print("结果已保存: results/test_predictions.png")
    plt.close()


def predict_image_file(image_path, model_path='results/best_model.pth'):
    """预测用户提供的图片"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    model = SimpleCNN(num_classes=2)
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.to(device)

    transform = transforms.Compose([
        transforms.Resize((28, 28)),
        transforms.ToTensor(),
    ])

    image = Image.open(image_path).convert('L')
    img_tensor = transform(image)

    pred, probs = predict_tensor(model, img_tensor, device)
    class_names = ['圆形', '方形']

    print(f"\n图片: {image_path}")
    print(f"预测: {class_names[pred]}")
    print(f"圆形: {probs[0]*100:.1f}%  方形: {probs[1]*100:.1f}%")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='圆形vs方形预测')
    parser.add_argument('--image', type=str, default=None, help='图片路径')
    parser.add_argument('--model', type=str, default='results/best_model.pth')
    parser.add_argument('--num', type=int, default=10)
    args = parser.parse_args()

    if args.image:
        predict_image_file(args.image, args.model)
    else:
        predict_random_samples(args.model, args.num)
