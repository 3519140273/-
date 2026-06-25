"""
工具函数：生成圆形vs方形数据集、训练可视化、结果保存
零下载，代码自动生成数据集
"""

import os
import torch
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def generate_shape_dataset(n_samples=6000, img_size=28, noise_level=0.05, seed=42):
    """
    生成圆形(标签0) vs 方形(标签1)数据集
    图片含随机位置、大小、旋转、噪声，全部在内存中生成
    """
    rng = np.random.RandomState(seed)
    images = []
    labels = []

    half = n_samples // 2

    for i in range(n_samples):
        img = np.zeros((img_size, img_size), dtype=np.float32)

        # 随机参数
        cx = rng.uniform(img_size * 0.25, img_size * 0.75)  # 中心x
        cy = rng.uniform(img_size * 0.25, img_size * 0.75)  # 中心y
        size = rng.uniform(img_size * 0.12, img_size * 0.32)  # 半径/半边长
        thickness = rng.uniform(1.2, 3.5)
        brightness = rng.uniform(0.6, 1.0)

        if i < half:
            # 圆形
            for y in range(img_size):
                for x in range(img_size):
                    dist = np.sqrt((x - cx)**2 + (y - cy)**2)
                    if abs(dist - size) < thickness:
                        img[y, x] = brightness
                        # 边缘羽化
                        edge_dist = abs(dist - size)
                        if edge_dist > thickness * 0.6:
                            img[y, x] *= 1 - (edge_dist - thickness * 0.6) / (thickness * 0.4)
            labels.append(0)
        else:
            # 方形 (带随机旋转)
            angle = rng.uniform(0, np.pi / 4)
            for y in range(img_size):
                for x in range(img_size):
                    dx = x - cx
                    dy = y - cy
                    rx = dx * np.cos(angle) + dy * np.sin(angle)
                    ry = -dx * np.sin(angle) + dy * np.cos(angle)
                    if abs(rx) < size and abs(ry) < size:
                        border_x = size - abs(rx)
                        border_y = size - abs(ry)
                        border = min(border_x, border_y)
                        if border < thickness:
                            img[y, x] = brightness * (border / thickness)
                        else:
                            img[y, x] = brightness
            labels.append(1)

        # 添加噪声
        img += rng.normal(0, noise_level, (img_size, img_size))
        img = np.clip(img, 0, 1)

        images.append(img)

    images = np.array(images)
    labels = np.array(labels)

    print(f"生成数据集: {n_samples} 张 {img_size}x{img_size} 灰度图")
    print(f"  圆形(标签0): {half} 张  方形(标签1): {half} 张")

    return images, labels


def get_data_loaders(batch_size=64, img_size=28, n_train=5000, n_val=1000,
                     noise_level=0.05):
    """
    生成训练/验证集，返回DataLoader
    """
    total = n_train + n_val
    images, labels = generate_shape_dataset(n_samples=total, img_size=img_size,
                                            noise_level=noise_level)

    # 转为PyTorch tensor: (N, 1, H, W)
    images_t = torch.tensor(images, dtype=torch.float32).unsqueeze(1)
    labels_t = torch.tensor(labels, dtype=torch.long)

    # 打乱 & 划分
    perm = torch.randperm(total)
    train_idx = perm[:n_train]
    val_idx = perm[n_train:]

    train_dataset = TensorDataset(images_t[train_idx], labels_t[train_idx])
    val_dataset = TensorDataset(images_t[val_idx], labels_t[val_idx])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    print(f"  训练集: {n_train} 张  验证集: {n_val} 张")
    return train_loader, val_loader


def show_sample_images(images, labels, num=8, save_path='samples.png'):
    """展示生成的样本图片"""
    fig, axes = plt.subplots(2, num//2, figsize=(12, 5))
    axes = axes.flatten()
    class_names = ['圆形', '方形']

    for i in range(num):
        idx = np.random.randint(0, len(images))
        axes[i].imshow(images[idx], cmap='gray')
        axes[i].set_title(class_names[labels[idx]])
        axes[i].axis('off')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"样本图片已保存: {save_path}")
    plt.close()


def plot_training_curves(history, save_path='training_curves.png'):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].plot(history['train_loss'], label='训练Loss', marker='o')
    axes[0].plot(history['val_loss'], label='验证Loss', marker='o')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('训练/验证 Loss 曲线')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(history['train_acc'], label='训练准确率', marker='o')
    axes[1].plot(history['val_acc'], label='验证准确率', marker='o')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy (%)')
    axes[1].set_title('训练/验证 准确率曲线')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"训练曲线已保存: {save_path}")
    plt.close()


def plot_confusion_matrix(all_labels, all_preds, class_names=['圆形', '方形'],
                          save_path='confusion_matrix.png'):
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)
    plt.xlabel('预测类别')
    plt.ylabel('真实类别')
    plt.title('混淆矩阵')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"混淆矩阵已保存: {save_path}")
    plt.close()
    return cm


def print_classification_report(all_labels, all_preds, class_names=['圆形', '方形']):
    report = classification_report(all_labels, all_preds,
                                   target_names=class_names, digits=4)
    print("\n" + "="*55)
    print("分类报告")
    print("="*55)
    print(report)
    return report


def visualize_predictions(model, dataloader, device,
                          class_names=['圆形', '方形'],
                          num_images=8, save_path='predictions.png'):
    model.eval()
    fig, axes = plt.subplots(2, 4, figsize=(12, 6))
    axes = axes.flatten()
    shown = 0

    with torch.no_grad():
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)

            for i in range(len(images)):
                if shown >= num_images:
                    break
                img = images[i].cpu().squeeze(0)
                true_label = class_names[labels[i].item()]
                pred_label = class_names[preds[i].item()]
                color = 'green' if labels[i] == preds[i] else 'red'
                axes[shown].imshow(img, cmap='gray')
                axes[shown].set_title(f'真:{true_label} 预:{pred_label}',
                                      color=color, fontsize=10)
                axes[shown].axis('off')
                shown += 1
            if shown >= num_images:
                break

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"预测示例已保存: {save_path}")
    plt.close()


def save_results(history, cm, report, save_dir='results'):
    os.makedirs(save_dir, exist_ok=True)
    with open(os.path.join(save_dir, 'training_history.txt'), 'w', encoding='utf-8') as f:
        f.write("Epoch | Train Loss | Val Loss | Train Acc(%) | Val Acc(%)\n")
        f.write("-" * 60 + "\n")
        for i in range(len(history['train_loss'])):
            f.write(f"{i+1:5d} | {history['train_loss'][i]:10.4f} | "
                    f"{history['val_loss'][i]:8.4f} | "
                    f"{history['train_acc'][i]:11.2f} | "
                    f"{history['val_acc'][i]:9.2f}\n")
    with open(os.path.join(save_dir, 'classification_report.txt'), 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"结果已保存到 {save_dir}/")
