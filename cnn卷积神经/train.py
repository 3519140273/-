"""
圆形vs方形 CNN 训练脚本 (零下载，代码生成数据)
用法:
    python train.py                      # 默认: 10 epochs
    python train.py --epochs 20          # 自定义epoch数
    python train.py --noise 0.1          # 调整噪声水平
    python train.py --n_train 8000       # 调整训练集大小
"""

import os
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm

from model import SimpleCNN
from utils import (
    get_data_loaders, show_sample_images, plot_training_curves,
    plot_confusion_matrix, print_classification_report,
    visualize_predictions, save_results, generate_shape_dataset
)


def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    pbar = tqdm(loader, desc='训练', leave=False)
    for images, labels in pbar:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

        pbar.set_postfix({'loss': f'{loss.item():.3f}',
                          'acc': f'{100.*correct/total:.1f}%'})

    return running_loss / len(loader), 100.0 * correct / total


@torch.no_grad()
def validate(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    all_preds, all_labels = [], []

    for images, labels in tqdm(loader, desc='验证', leave=False):
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        loss = criterion(outputs, labels)

        running_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

        all_preds.extend(predicted.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

    return (running_loss / len(loader), 100.0 * correct / total,
            all_labels, all_preds)


def main():
    parser = argparse.ArgumentParser(description='圆形vs方形 CNN训练')
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--batch_size', type=int, default=64)
    parser.add_argument('--lr', type=float, default=0.001)
    parser.add_argument('--n_train', type=int, default=5000)
    parser.add_argument('--n_val', type=int, default=1000)
    parser.add_argument('--noise', type=float, default=0.05)
    parser.add_argument('--output_dir', type=str, default='./results')
    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")

    # ========== 1. 生成数据 ==========
    print(f"\n[数据] 生成圆形vs方形数据集 (噪声={args.noise})...")
    train_loader, val_loader = get_data_loaders(
        batch_size=args.batch_size,
        n_train=args.n_train,
        n_val=args.n_val,
        noise_level=args.noise
    )

    # 保存样本图
    os.makedirs(args.output_dir, exist_ok=True)
    img_batch, label_batch = next(iter(train_loader))
    show_sample_images(img_batch.squeeze(1).numpy(), label_batch.numpy(),
                       save_path=os.path.join(args.output_dir, 'samples.png'))

    # ========== 2. 创建模型 ==========
    print(f"\n[模型] SimpleCNN (2分类)")
    model = SimpleCNN(num_classes=2).to(device)
    print(f"参数量: {sum(p.numel() for p in model.parameters()):,}")

    # ========== 3. 损失函数 & 优化器 ==========
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    # ========== 4. 训练 ==========
    print(f"\n[训练] 开始 ({args.epochs} epochs)")
    print("=" * 60)

    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
    best_acc = 0.0

    for epoch in range(args.epochs):
        print(f"\nEpoch {epoch+1}/{args.epochs}")

        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device)
        val_loss, val_acc, val_labels, val_preds = validate(
            model, val_loader, criterion, device)

        scheduler.step()

        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_acc'].append(train_acc)
        history['val_acc'].append(val_acc)

        print(f"  训练 Loss: {train_loss:.4f}  Acc: {train_acc:.2f}%")
        print(f"  验证 Loss: {val_loss:.4f}  Acc: {val_acc:.2f}%")

        if val_acc > best_acc:
            best_acc = val_acc
            os.makedirs(args.output_dir, exist_ok=True)
            torch.save(model.state_dict(),
                       os.path.join(args.output_dir, 'best_model.pth'))
            print(f"  [OK] 新最佳模型! 准确率: {best_acc:.2f}%")

    print("\n" + "=" * 60)
    print(f"[完成] 训练结束! 最佳准确率: {best_acc:.2f}%")

    # ========== 5. 评估 ==========
    print("\n[评估] 生成报告...")
    os.makedirs(args.output_dir, exist_ok=True)

    model.load_state_dict(torch.load(
        os.path.join(args.output_dir, 'best_model.pth'), weights_only=True))
    _, _, all_labels, all_preds = validate(model, val_loader, criterion, device)

    plot_training_curves(history,
                         save_path=os.path.join(args.output_dir, 'training_curves.png'))
    cm = plot_confusion_matrix(all_labels, all_preds,
                               save_path=os.path.join(args.output_dir, 'confusion_matrix.png'))
    report = print_classification_report(all_labels, all_preds)
    visualize_predictions(model, val_loader, device,
                          save_path=os.path.join(args.output_dir, 'predictions.png'))
    save_results(history, cm, report, save_dir=args.output_dir)

    print("\n[完成] 查看 results/ 目录:")
    print("   samples.png              - 数据样本")
    print("   training_curves.png      - 训练曲线")
    print("   confusion_matrix.png     - 混淆矩阵")
    print("   predictions.png          - 预测示例")
    print("   training_history.txt     - 训练记录")
    print("   classification_report.txt - 分类报告")
    print("   best_model.pth           - 模型权重")


if __name__ == '__main__':
    main()
