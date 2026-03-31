"""
Full Fine-Tuning Pipeline for Indian Cattle Breed Classifier
============================================================
Strategy:
  1. Load existing ResNet50 weights (newmodel.pth) as warm start
  2. Progressive unfreezing: start with fc → layer4 → layer3
  3. Cosine annealing with warm restarts
  4. MixUp augmentation for better generalization
  5. Aggressive augmentation for weak classes
  6. WeightedRandomSampler with strong boosting for underperformers
  7. Label smoothing loss
  8. Test-Time Augmentation (TTA) for final evaluation
  9. Auto-saves best model by validation accuracy
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
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────
# Known weak breeds from baseline evaluation
# ─────────────────────────────────────────────────────────
WEAK_BREEDS = {
    "Deoni", "Hariana", "Nari", "Nimari", "Tharparkar", "Kankrej",
    "ghumsari", "Khillari", "bachaur", "Hallikar", "dagri",
    "Amritmahal", "gaolao", "kherigarh", "Ongole", "Shweta",
    "Krishna_Valley", "Red_Sindhi", "malvi", "gangatari", "nagori",
    "badri", "Malnad_gidda", "Khariar"
}


# ─────────────────────────────────────────────────────────
# EarlyStopping (accuracy-based)
# ─────────────────────────────────────────────────────────
class EarlyStopping:
    def __init__(self, patience=10, min_delta=0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.best_acc = 0.0
        self.counter = 0
        self.early_stop = False

    def __call__(self, val_acc, model, path):
        if val_acc > self.best_acc + self.min_delta:
            self.best_acc = val_acc
            torch.save(model.state_dict(), path)
            print(f"  ✅ Val acc improved → {val_acc*100:.2f}%. Model saved.")
            self.counter = 0
        else:
            self.counter += 1
            print(f"  ⏳ No improvement {self.counter}/{self.patience} (best: {self.best_acc*100:.2f}%)")
            if self.counter >= self.patience:
                self.early_stop = True


# ─────────────────────────────────────────────────────────
# MixUp augmentation
# ─────────────────────────────────────────────────────────
def mixup_data(x, y, alpha=0.2, device='cuda'):
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1
    batch_size = x.size(0)
    index = torch.randperm(batch_size).to(device)
    mixed_x = lam * x + (1 - lam) * x[index]
    y_a, y_b = y, y[index]
    return mixed_x, y_a, y_b, lam


def mixup_criterion(criterion, pred, y_a, y_b, lam):
    return lam * criterion(pred, y_a) + (1 - lam) * criterion(pred, y_b)


# ─────────────────────────────────────────────────────────
# Dataset utilities
# ─────────────────────────────────────────────────────────
class SmartTransformSubset(torch.utils.data.Dataset):
    """Applies strong augmentation to weak breeds, mild to others."""
    def __init__(self, subset, weak_class_ids, strong_aug, mild_aug):
        self.subset = subset
        self.weak_ids = weak_class_ids
        self.strong_aug = strong_aug
        self.mild_aug = mild_aug

    def __getitem__(self, index):
        x, y = self.subset[index]
        transform = self.strong_aug if y in self.weak_ids else self.mild_aug
        return transform(x), y

    def __len__(self):
        return len(self.subset)


class TransformedSubset(torch.utils.data.Dataset):
    def __init__(self, subset, transform):
        self.subset = subset
        self.transform = transform

    def __getitem__(self, index):
        x, y = self.subset[index]
        return self.transform(x), y

    def __len__(self):
        return len(self.subset)


# ─────────────────────────────────────────────────────────
# Training utilities
# ─────────────────────────────────────────────────────────
def plot_history(history, save_path):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].plot(history['train_loss'], label='Train', color='#2196F3')
    axes[0].plot(history['val_loss'], label='Val', color='#F44336')
    axes[0].set_title('Loss History', fontsize=14)
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot([a * 100 for a in history['train_acc']], label='Train', color='#2196F3')
    axes[1].plot([a * 100 for a in history['val_acc']], label='Val', color='#F44336')
    axes[1].set_title('Accuracy History', fontsize=14)
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy (%)')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"Training history saved: {save_path}")
    plt.close()


def set_trainable(model, layer_names):
    """Set specific layers as trainable, freeze rest."""
    for name, param in model.named_parameters():
        param.requires_grad = any(ln in name for ln in layer_names)

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    frozen = sum(p.numel() for p in model.parameters() if not p.requires_grad)
    print(f"  Trainable: {trainable:,} | Frozen: {frozen:,}")


def evaluate_full(model, dataloader, device, class_names, weak_indices):
    """Full evaluation with per-class metrics."""
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)

    overall_acc = (all_preds == all_labels).mean()
    print(f"\n📊 Overall Validation Accuracy: {overall_acc*100:.2f}%")

    # Per-class precision, recall, f1
    report = classification_report(
        all_labels, all_preds, target_names=class_names,
        zero_division=0, digits=3
    )
    print("\n[Full Classification Report]")
    print(report)

    # Weak breed summary
    print(f"\n{'='*55}")
    print("📌 Weak Breed Performance:")
    print(f"{'Breed':<25} {'F1':>6} {'Prec':>7} {'Recall':>8}")
    print('-' * 50)
    prec_arr = precision_score(all_labels, all_preds, average=None, zero_division=0)
    rec_arr = recall_score(all_labels, all_preds, average=None, zero_division=0)

    for idx in sorted(weak_indices):
        if idx >= len(class_names):
            continue
        mask = all_labels == idx
        if mask.sum() == 0:
            continue
        f1 = f1_score(all_labels[mask], all_preds[mask], average='micro', zero_division=0)
        print(f"  {class_names[idx]:<23} {f1*100:>5.1f}%  {prec_arr[idx]*100:>5.1f}%  {rec_arr[idx]*100:>6.1f}%")

    return overall_acc, all_preds, all_labels


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Fine-tune Cattle Breed Classifier')
    parser.add_argument('--data_dir',   type=str,   default='/home/punith/antigravity/hemanth-prj/data/cattle')
    parser.add_argument('--base_model', type=str,   default='/home/punith/antigravity/hemanth-prj/models/newmodel.pth')
    parser.add_argument('--save_path',  type=str,   default='/home/punith/antigravity/hemanth-prj/models/finetuned_v2.pth')
    parser.add_argument('--batch_size', type=int,   default=32)
    parser.add_argument('--epochs',     type=int,   default=50)
    parser.add_argument('--lr',         type=float, default=5e-4)
    parser.add_argument('--weak_boost', type=float, default=4.0)
    parser.add_argument('--mixup_alpha',type=float, default=0.2)
    parser.add_argument('--resume',     type=str,   default=None,
                        help='Resume from checkpoint instead of base_model')
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n{'='*60}")
    print(f"  🐄 Cattle Breed Fine-Tuning v2 — Device: {device}")
    print(f"{'='*60}")
    if device.type == 'cuda':
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
        print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    # ── Transforms ─────────────────────────────────────────
    normalize = transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])

    strong_aug = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.55, 1.0), ratio=(0.75, 1.33)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(p=0.08),
        transforms.RandomRotation(35),
        transforms.ColorJitter(brightness=0.5, contrast=0.5, saturation=0.4, hue=0.15),
        transforms.RandomAffine(degrees=0, translate=(0.15, 0.15), shear=10),
        transforms.RandomGrayscale(p=0.05),
        transforms.ToTensor(),
        normalize,
        transforms.RandomErasing(p=0.35, scale=(0.02, 0.30)),
    ])

    mild_aug = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        normalize,
    ])

    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        normalize,
    ])

    # ── Load Dataset ────────────────────────────────────────
    print(f"\n[1] 📂 Loading dataset from: {args.data_dir}")
    full_dataset = datasets.ImageFolder(args.data_dir)
    class_names = full_dataset.classes
    targets = full_dataset.targets
    num_classes = len(class_names)
    print(f"    Classes: {num_classes} | Total images: {len(full_dataset)}")

    # Identify weak breed indices
    weak_indices = {i for i, name in enumerate(class_names)
                    if any(w.lower() in name.lower() for w in WEAK_BREEDS)}
    print(f"\n[2] 🎯 Weak breeds detected ({len(weak_indices)} classes):")
    class_counts = Counter(targets)
    for idx in sorted(weak_indices):
        print(f"    {class_names[idx]:<25}: {class_counts[idx]} images")

    # ── Train/Val Split ─────────────────────────────────────
    train_idx, val_idx = train_test_split(
        list(range(len(full_dataset))), test_size=0.2,
        random_state=42, stratify=targets
    )
    train_targets = [targets[i] for i in train_idx]

    # ── Weighted Sampler ────────────────────────────────────
    print(f"\n[3] ⚖️  Computing sample weights (weak_boost={args.weak_boost}x)...")
    classes_arr = np.unique(train_targets)
    base_weights = compute_class_weight(class_weight='balanced', classes=classes_arr, y=train_targets)
    boosted_weights = base_weights.copy()
    for idx in weak_indices:
        if idx < len(boosted_weights):
            boosted_weights[idx] *= args.weak_boost

    sample_weights = [boosted_weights[t] for t in train_targets]
    sampler = WeightedRandomSampler(sample_weights, num_samples=len(sample_weights), replacement=True)

    # ── Build Datasets ──────────────────────────────────────
    train_subset = Subset(full_dataset, train_idx)
    val_subset = Subset(full_dataset, val_idx)

    train_dataset = SmartTransformSubset(train_subset, weak_indices, strong_aug, mild_aug)
    val_dataset = TransformedSubset(val_subset, val_transform)

    dataloaders = {
        'train': DataLoader(train_dataset, batch_size=args.batch_size,
                            sampler=sampler, num_workers=4, pin_memory=True),
        'val':   DataLoader(val_dataset,   batch_size=args.batch_size,
                            shuffle=False, num_workers=4, pin_memory=True),
    }
    dataset_sizes = {'train': len(train_idx), 'val': len(val_idx)}
    print(f"\n    Train: {len(train_idx)} | Val: {len(val_idx)}")

    # ── Load Model ──────────────────────────────────────────
    src = args.resume if args.resume else args.base_model
    print(f"\n[4] 🔄 Loading model from: {src}")
    model = models.resnet50(weights=None)
    model.fc = nn.Sequential(
        nn.BatchNorm1d(model.fc.in_features),
        nn.Dropout(0.5),
        nn.Linear(model.fc.in_features, 512),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(512, num_classes)
    )

    # Load state dict — handle fc layer mismatch gracefully
    checkpoint = torch.load(src, map_location=device, weights_only=True)
    model_dict = model.state_dict()
    # Filter out mismatched keys (e.g. old fc shape)
    filtered = {k: v for k, v in checkpoint.items()
                if k in model_dict and v.shape == model_dict[k].shape}
    skipped = set(checkpoint.keys()) - set(filtered.keys())
    if skipped:
        print(f"    ⚠️  Skipped {len(skipped)} mismatched keys: {list(skipped)[:5]}...")
    model_dict.update(filtered)
    model.load_state_dict(model_dict, strict=False)
    model = model.to(device)
    print(f"    ✅ Model loaded. Parameters: {sum(p.numel() for p in model.parameters()):,}")

    # ── Loss & Optimizer ────────────────────────────────────
    criterion = nn.CrossEntropyLoss(label_smoothing=0.05)

    # ══════════════════════════════════════════════════════════
    # Phase 1: Train only FC head (1-3 epochs warm-up)
    # ══════════════════════════════════════════════════════════
    print(f"\n{'='*60}")
    print("  📍 PHASE 1: Warm-up FC head only (3 epochs)")
    print(f"{'='*60}")

    set_trainable(model, ['fc'])
    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=1e-3, weight_decay=1e-4
    )
    scheduler = optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=1e-3,
        steps_per_epoch=len(dataloaders['train']),
        epochs=3, pct_start=0.3
    )

    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
    early_stop = EarlyStopping(patience=args.epochs // 5)  # generous patience for phase 1

    for epoch in range(3):
        print(f"\nEpoch {epoch+1}/3 [PHASE 1]")
        print('-' * 40)
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
                        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                        optimizer.step()
                        scheduler.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]
            print(f"  {phase.upper()} Loss: {epoch_loss:.4f}  Acc: {epoch_acc*100:.2f}%")
            history[f'{phase}_loss'].append(epoch_loss)
            history[f'{phase}_acc'].append(epoch_acc.item())

            if phase == 'val':
                early_stop(epoch_acc.item(), model, args.save_path)

    # ══════════════════════════════════════════════════════════
    # Phase 2: Unfreeze layer4 + fc (main fine-tuning)
    # ══════════════════════════════════════════════════════════
    print(f"\n{'='*60}")
    print(f"  📍 PHASE 2: Fine-tune layer4 + fc ({args.epochs} epochs)")
    print(f"{'='*60}")

    set_trainable(model, ['layer4', 'fc'])
    optimizer = optim.AdamW([
        {'params': [p for n, p in model.named_parameters()
                    if 'layer4' in n and p.requires_grad], 'lr': args.lr * 0.1},
        {'params': [p for n, p in model.named_parameters()
                    if 'fc' in n and p.requires_grad], 'lr': args.lr},
    ], weight_decay=1e-4)

    # Cosine Annealing with warm restarts
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=10, T_mult=2, eta_min=1e-6
    )

    early_stop = EarlyStopping(patience=12)
    since = time.time()
    use_mixup = args.mixup_alpha > 0

    for epoch in range(args.epochs):
        lr_fc = optimizer.param_groups[-1]['lr']
        print(f"\nEpoch {epoch+1}/{args.epochs} | LR(fc): {lr_fc:.2e}")
        print('-' * 45)

        for phase in ['train', 'val']:
            model.train() if phase == 'train' else model.eval()
            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloaders[phase]:
                inputs, labels = inputs.to(device), labels.to(device)
                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == 'train'):
                    if phase == 'train' and use_mixup and np.random.random() < 0.5:
                        # Apply MixUp on 50% of batches
                        inputs, labels_a, labels_b, lam = mixup_data(
                            inputs, labels, args.mixup_alpha, device)
                        outputs = model(inputs)
                        loss = mixup_criterion(criterion, outputs, labels_a, labels_b, lam)
                        _, preds = torch.max(outputs, 1)
                        corrects = (lam * (preds == labels_a).float() +
                                    (1 - lam) * (preds == labels_b).float()).sum()
                    else:
                        outputs = model(inputs)
                        _, preds = torch.max(outputs, 1)
                        loss = criterion(outputs, labels)
                        corrects = torch.sum(preds == labels.data).float()

                    if phase == 'train':
                        loss.backward()
                        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += corrects.item()

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects / dataset_sizes[phase]
            print(f"  {phase.upper()} Loss: {epoch_loss:.4f}  Acc: {epoch_acc*100:.2f}%")
            history[f'{phase}_loss'].append(epoch_loss)
            history[f'{phase}_acc'].append(epoch_acc)

            if phase == 'val':
                scheduler.step()
                early_stop(epoch_acc, model, args.save_path)
                if early_stop.early_stop:
                    print("\n⛔ Early stopping triggered.")
                    break
        else:
            continue
        break

    # ══════════════════════════════════════════════════════════
    # Phase 3 (optional): Unfreeze layer3 for further refinement
    # ══════════════════════════════════════════════════════════
    remaining_epochs = max(0, 10 - early_stop.counter)
    if remaining_epochs > 0 and not early_stop.early_stop:
        print(f"\n{'='*60}")
        print(f"  📍 PHASE 3: Fine-tune layer3+4+fc ({remaining_epochs} epochs)")
        print(f"{'='*60}")

        set_trainable(model, ['layer3', 'layer4', 'fc'])
        model.load_state_dict(torch.load(args.save_path, map_location=device, weights_only=True))
        model = model.to(device)

        optimizer3 = optim.AdamW([
            {'params': [p for n, p in model.named_parameters()
                        if 'layer3' in n and p.requires_grad], 'lr': args.lr * 0.01},
            {'params': [p for n, p in model.named_parameters()
                        if 'layer4' in n and p.requires_grad], 'lr': args.lr * 0.05},
            {'params': [p for n, p in model.named_parameters()
                        if 'fc' in n and p.requires_grad], 'lr': args.lr * 0.1},
        ], weight_decay=1e-4)

        scheduler3 = optim.lr_scheduler.CosineAnnealingLR(
            optimizer3, T_max=remaining_epochs, eta_min=1e-7)
        early_stop3 = EarlyStopping(patience=5)

        for epoch in range(remaining_epochs):
            print(f"\nEpoch {epoch+1}/{remaining_epochs} [PHASE 3]")
            for phase in ['train', 'val']:
                model.train() if phase == 'train' else model.eval()
                running_loss = 0.0
                running_corrects = 0

                for inputs, labels in dataloaders[phase]:
                    inputs, labels = inputs.to(device), labels.to(device)
                    optimizer3.zero_grad()
                    with torch.set_grad_enabled(phase == 'train'):
                        outputs = model(inputs)
                        _, preds = torch.max(outputs, 1)
                        loss = criterion(outputs, labels)
                        if phase == 'train':
                            loss.backward()
                            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
                            optimizer3.step()

                    running_loss += loss.item() * inputs.size(0)
                    running_corrects += torch.sum(preds == labels.data).item()

                epoch_loss = running_loss / dataset_sizes[phase]
                epoch_acc = running_corrects / dataset_sizes[phase]
                print(f"  {phase.upper()} Loss: {epoch_loss:.4f}  Acc: {epoch_acc*100:.2f}%")
                history[f'{phase}_loss'].append(epoch_loss)
                history[f'{phase}_acc'].append(epoch_acc)

                if phase == 'val':
                    scheduler3.step()
                    early_stop3(epoch_acc, model, args.save_path)
                    if early_stop3.early_stop:
                        print("\n⛔ Phase 3 early stopping.")
                        break
            else:
                continue
            break

    elapsed = time.time() - since
    print(f"\n✅ Fine-tuning complete in {elapsed//60:.0f}m {elapsed%60:.0f}s")
    print(f"   Best val accuracy: {max(early_stop.best_acc, getattr(locals().get('early_stop3', early_stop), 'best_acc', 0))*100:.2f}%")

    # ── Save training history plot ──────────────────────────
    os.makedirs('reports', exist_ok=True)
    plot_history(history, '/home/punith/antigravity/hemanth-prj/reports/finetune_v2_history.png')

    # ── Final evaluation ────────────────────────────────────
    print(f"\n{'='*60}")
    print("[6] 📊 Final evaluation on validation set...")
    model.load_state_dict(torch.load(args.save_path, map_location=device, weights_only=True))
    model = model.to(device)
    overall_acc, preds, labels_arr = evaluate_full(model, dataloaders['val'], device, class_names, weak_indices)

    # Save classification report
    report = classification_report(labels_arr, preds, target_names=class_names, zero_division=0, digits=3)
    report_path = '/home/punith/antigravity/hemanth-prj/reports/finetune_v2_report.txt'
    with open(report_path, 'w') as f:
        f.write(f"Fine-Tuned Model v2 — Validation Accuracy: {overall_acc*100:.2f}%\n\n")
        f.write(report)
    print(f"\n📄 Classification report saved: {report_path}")
    print(f"💾 Fine-tuned model saved: {args.save_path}")


if __name__ == '__main__':
    main()
