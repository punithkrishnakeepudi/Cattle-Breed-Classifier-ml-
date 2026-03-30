"""
Fine-tune script for low-performing breeds.
Strategy:
  - Freeze backbone (layer1, layer2, layer3)
  - Only train layer4 + fc on the WEAK breeds' data
  - Use higher LR for fc, lower for layer4
  - Apply aggressive augmentation for the weak classes only
  - WeightedRandomSampler focused on weak breeds
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torchvision.models import ResNet50_Weights
from torch.utils.data import DataLoader, Subset, WeightedRandomSampler
import numpy as np
import os
import copy
import time
import argparse
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report
from collections import Counter
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────
# Weak breeds (confirmed from evaluation report)
# ─────────────────────────────────────────────
WEAK_BREEDS = {
    "Deoni", "Hariana", "Nari", "Nimari", "Tharparkar", "Kankrej",
    "ghumsari", "Khillari", "bachaur", "Hallikar", "dagri",
    "Amritmahal", "gaolao", "kherigarh", "Ongole", "Shweta Kapila",
    "Krishna_Valley", "Red_Sindhi", "malvi", "gangatari", "nagori"
}

# ─────────────────────────────────────────────
# EarlyStopping
# ─────────────────────────────────────────────
class EarlyStopping:
    def __init__(self, patience=7):
        self.patience = patience
        self.best_acc = 0.0
        self.counter = 0
        self.early_stop = False

    def __call__(self, val_acc, model, path):
        if val_acc > self.best_acc:
            self.best_acc = val_acc
            torch.save(model.state_dict(), path)
            print(f"  ✅ Val acc improved → {val_acc:.4f}. Model saved.")
            self.counter = 0
        else:
            self.counter += 1
            print(f"  ⏳ No improvement ({self.counter}/{self.patience})")
            if self.counter >= self.patience:
                self.early_stop = True


class TransformedSubset(torch.utils.data.Dataset):
    def __init__(self, subset, transform=None):
        self.subset = subset
        self.transform = transform

    def __getitem__(self, index):
        x, y = self.subset[index]
        if self.transform:
            x = self.transform(x)
        return x, y

    def __len__(self):
        return len(self.subset)


def plot_history(history, save_path):
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history['train_loss'], label='Train Loss')
    plt.plot(history['val_loss'], label='Val Loss')
    plt.title('Loss'); plt.legend()
    plt.subplot(1, 2, 2)
    plt.plot(history['train_acc'], label='Train Acc')
    plt.plot(history['val_acc'], label='Val Acc')
    plt.title('Accuracy'); plt.legend()
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"Training history saved: {save_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir',   type=str,   default='/home/punith/antigravity/hemanth-prj/data/cattle')
    parser.add_argument('--base_model', type=str,   default='/home/punith/antigravity/hemanth-prj/models/newmodel.pth')
    parser.add_argument('--save_path',  type=str,   default='/home/punith/antigravity/hemanth-prj/models/finetuned_model.pth')
    parser.add_argument('--batch_size', type=int,   default=32)
    parser.add_argument('--epochs',     type=int,   default=30)
    parser.add_argument('--lr_fc',      type=float, default=1e-3,  help='LR for classifier head')
    parser.add_argument('--lr_layer4',  type=float, default=1e-4,  help='LR for layer4')
    parser.add_argument('--weak_boost', type=float, default=3.0,   help='Extra weight multiplier for weak breeds in sampler')
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n{'='*55}")
    print(f"  Fine-Tuning Pipeline — device: {device}")
    print(f"{'='*55}")

    # ── Transforms ──────────────────────────────────────────
    # Strong augmentation for weak breeds, mild for others
    strong_aug = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.6, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(p=0.1),
        transforms.RandomRotation(30),
        transforms.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4, hue=0.15),
        transforms.RandomAffine(degrees=0, translate=(0.15, 0.15)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        transforms.RandomErasing(p=0.3, scale=(0.02, 0.25)),
    ])
    mild_aug = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    # ── Dataset ─────────────────────────────────────────────
    print("\n[1] Loading dataset...")
    full_dataset = datasets.ImageFolder(args.data_dir)
    class_names  = full_dataset.classes
    targets      = full_dataset.targets
    num_classes  = len(class_names)
    print(f"    Classes: {num_classes} | Total images: {len(full_dataset)}")

    # Print weak breed image counts
    print("\n[2] Weak breed image counts:")
    class_counts = Counter(targets)
    weak_indices = {i for i, name in enumerate(class_names) if name in WEAK_BREEDS}
    for idx in sorted(weak_indices):
        print(f"    {class_names[idx]:25s}: {class_counts[idx]} images")

    # ── Train / Val split ────────────────────────────────────
    train_idx, val_idx = train_test_split(
        list(range(len(full_dataset))), test_size=0.2,
        random_state=42, stratify=targets
    )
    train_targets = [targets[i] for i in train_idx]

    # ── Weighted sampler with BOOST for weak breeds ──────────
    print(f"\n[3] Computing sample weights (weak_boost={args.weak_boost}x)...")
    classes = np.unique(train_targets)
    base_weights = compute_class_weight(class_weight='balanced', classes=classes, y=train_targets)

    # Boost weak breed weights extra
    boosted_weights = base_weights.copy()
    for idx in weak_indices:
        if idx < len(boosted_weights):
            boosted_weights[idx] *= args.weak_boost

    sample_weights = [boosted_weights[t] for t in train_targets]
    sampler = WeightedRandomSampler(sample_weights, num_samples=len(sample_weights), replacement=True)

    # ── Per-sample transform based on weak/strong ────────────
    class SmartTransformSubset(torch.utils.data.Dataset):
        def __init__(self, subset, weak_class_ids):
            self.subset = subset
            self.weak_ids = weak_class_ids
        def __getitem__(self, index):
            x, y = self.subset[index]
            transform = strong_aug if y in self.weak_ids else mild_aug
            return transform(x), y
        def __len__(self):
            return len(self.subset)

    train_subset = Subset(full_dataset, train_idx)
    val_subset   = Subset(full_dataset, val_idx)

    train_dataset = SmartTransformSubset(train_subset, weak_indices)
    val_dataset   = TransformedSubset(val_subset, val_transform)

    dataloaders = {
        'train': DataLoader(train_dataset, batch_size=args.batch_size, sampler=sampler, num_workers=4, pin_memory=True),
        'val':   DataLoader(val_dataset,   batch_size=args.batch_size, shuffle=False,  num_workers=4, pin_memory=True),
    }
    dataset_sizes = {'train': len(train_idx), 'val': len(val_idx)}

    # ── Model: load existing weights ─────────────────────────
    print(f"\n[4] Loading base model from: {args.base_model}")
    model = models.resnet50(weights=None)
    model.fc = nn.Sequential(nn.Dropout(0.5), nn.Linear(model.fc.in_features, num_classes))
    model.load_state_dict(torch.load(args.base_model, map_location=device, weights_only=True))
    model = model.to(device)

    # ── Freeze strategy ──────────────────────────────────────
    # Freeze: conv1, bn1, layer1, layer2, layer3
    # Unfreeze: layer4 + fc
    for name, param in model.named_parameters():
        if any(x in name for x in ['conv1', 'bn1', 'layer1', 'layer2', 'layer3']):
            param.requires_grad = False
        else:
            param.requires_grad = True

    frozen = sum(p.numel() for p in model.parameters() if not p.requires_grad)
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"    Frozen params:    {frozen:,}")
    print(f"    Trainable params: {trainable:,}")

    # ── Optimizer with layer-specific LRs ────────────────────
    optimizer = optim.Adam([
        {'params': model.layer4.parameters(), 'lr': args.lr_layer4},
        {'params': model.fc.parameters(),     'lr': args.lr_fc},
    ], weight_decay=1e-4)

    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.05)

    # ── Training loop ────────────────────────────────────────
    print(f"\n[5] Starting fine-tuning for {args.epochs} epochs...\n")
    early_stop = EarlyStopping(patience=8)
    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
    since = time.time()

    for epoch in range(args.epochs):
        print(f"Epoch {epoch+1}/{args.epochs} — LR(fc): {optimizer.param_groups[1]['lr']:.2e}")
        print('-' * 45)

        for phase in ['train', 'val']:
            model.train() if phase == 'train' else model.eval()
            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloaders[phase]:
                inputs, labels = inputs.to(device), labels.to(device)
                optimizer.zero_grad()
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc  = running_corrects.double() / dataset_sizes[phase]
            print(f"  {phase.upper()} Loss: {epoch_loss:.4f}  Acc: {epoch_acc:.4f}")

            history[f'{phase}_loss'].append(epoch_loss)
            history[f'{phase}_acc'].append(epoch_acc.item())

            if phase == 'val':
                scheduler.step()
                early_stop(epoch_acc.item(), model, args.save_path)
                if early_stop.early_stop:
                    print("\n⛔ Early stopping triggered.")
                    break
        else:
            continue
        break

    elapsed = time.time() - since
    print(f"\n✅ Fine-tuning complete in {elapsed//60:.0f}m {elapsed%60:.0f}s")
    print(f"   Best val accuracy: {early_stop.best_acc:.4f} ({early_stop.best_acc*100:.1f}%)")

    # ── Save history plot ────────────────────────────────────
    os.makedirs('reports', exist_ok=True)
    plot_history(history, 'reports/finetune_history.png')

    # ── Final evaluation ─────────────────────────────────────
    print("\n[6] Final evaluation on validation set...")
    model.load_state_dict(torch.load(args.save_path, map_location=device, weights_only=True))
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for inputs, labels in dataloaders['val']:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())

    # Only print weak breed stats
    print("\n📊 Weak Breed Results After Fine-Tuning:")
    from sklearn.metrics import f1_score, precision_score, recall_score
    print(f"{'Breed':<25} {'F1':>6} {'Precision':>10} {'Recall':>8}")
    print('-' * 55)
    for idx in sorted(weak_indices):
        name = class_names[idx]
        mask = np.array(all_labels) == idx
        if mask.sum() == 0:
            continue
        pred_mask = np.array(all_preds)
        f1  = f1_score(np.array(all_labels)[mask], pred_mask[mask], average='micro', zero_division=0)
        prec = precision_score(np.array(all_labels), pred_mask, average=None, zero_division=0)[idx]
        rec  = recall_score(np.array(all_labels), pred_mask, average=None, zero_division=0)[idx]
        print(f"  {name:<23} {f1*100:>5.1f}%  {prec*100:>8.1f}%  {rec*100:>7.1f}%")

    print(f"\nFine-tuned model saved → {args.save_path}")
    print("Run evaluate_model.py --model finetuned_model.pth for full report.")


if __name__ == '__main__':
    main()
