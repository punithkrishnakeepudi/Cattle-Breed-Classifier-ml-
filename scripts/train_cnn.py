import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torchvision.models import ResNet50_Weights
from torch.utils.data import DataLoader, Subset, WeightedRandomSampler
import matplotlib.pyplot as plt
import os
import time
import copy
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import warnings
from collections import Counter
import argparse

warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')

def evaluate_and_analyze(model, dataloader, device, class_names):
    print("\n--- Evaluation & Analysis ---")
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
    # 5. DEBUGGING & ANALYSIS
    pred_counts = Counter(all_preds)
    actual_counts = Counter(all_labels)
    
    print("\n[Prediction Distribution (Validation Set)]")
    for i, name in enumerate(class_names):
        print(f"{name}: Actual={actual_counts[i]}, Predicted={pred_counts[i]}")
        
    zero_pred_classes = [name for i, name in enumerate(class_names) if pred_counts[i] == 0]
    if zero_pred_classes:
        print(f"\n[WARNING] Classes never predicted ({len(zero_pred_classes)} classes):")
        print(", ".join(zero_pred_classes))
        print("\nSuggestions if imbalance still exists:")
        print("1. Collect more images for the unpredicted classes.")
        print("2. Increase data augmentation specifically for minority classes.")
        print("3. Try explicitly upsampling minority classes before passing to the framework.")
        print("4. Tune learning rate and batch size further.")
        print("5. Enhance feature extraction by unfreezing more layers in ResNet50.")

    # 6. EVALUATION METRICS
    print("\n[Classification Report]")
    # Zero division handled internally by zero_division=0
    report = classification_report(all_labels, all_preds, target_names=class_names, zero_division=0)
    print(report)
    
    # Generate Confusion Matrix
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(20, 20))
    sns.heatmap(cm, annot=False, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.savefig('newmodel_confusion_matrix.png')
    print("\nConfusion matrix saved as newmodel_confusion_matrix.png")


class EarlyStopping:
    def __init__(self, patience=7, delta=0.0):
        self.patience = patience
        self.delta = delta
        self.best_loss = None
        self.early_stop = False
        self.counter = 0

    def __call__(self, val_loss, model, path='cnn_model.pth'):
        if self.best_loss is None:
            self.best_loss = val_loss
            self.save_checkpoint(val_loss, model, path)
        elif val_loss > self.best_loss - self.delta:
            self.counter += 1
            print(f'EarlyStopping counter: {self.counter} out of {self.patience}')
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            self.save_checkpoint(val_loss, model, path)
            self.counter = 0

    def save_checkpoint(self, val_loss, model, path):
        print(f'Validation loss decreased; saving model to {path}...')
        torch.save(model.state_dict(), path)


def train_model(model, criterion, optimizer, scheduler, dataloaders, dataset_sizes, device, num_epochs=25, model_path='cnn_model.pth'):
    since = time.time()
    best_model_wts = copy.deepcopy(model.state_dict())
    
    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
    early_stopping = EarlyStopping(patience=10, delta=0.001)

    for epoch in range(num_epochs):
        print(f'\nEpoch {epoch+1}/{num_epochs}')
        print('-' * 10)

        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

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
            epoch_acc = running_corrects.double() / dataset_sizes[phase]

            print(f'{phase.capitalize()} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')
            
            history[f'{phase}_loss'].append(epoch_loss)
            history[f'{phase}_acc'].append(epoch_acc.item())

            if phase == 'val':
                scheduler.step(epoch_loss)
                early_stopping(epoch_loss, model, path=model_path)
                if early_stopping.early_stop:
                    print("Early stopping triggered")
                    model.load_state_dict(torch.load(model_path, weights_only=True))
                    time_elapsed = time.time() - since
                    print(f'Training complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
                    return model, history

    time_elapsed = time.time() - since
    print(f'Training complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
    
    # Load best model weights
    try:
        model.load_state_dict(torch.load(model_path, weights_only=True))
    except (FileNotFoundError, RuntimeError):
        pass
        
    return model, history

def plot_history(history):
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history['train_loss'], label='Train Loss')
    plt.plot(history['val_loss'], label='Val Loss')
    plt.title('Loss History')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(history['train_acc'], label='Train Acc')
    plt.plot(history['val_acc'], label='Val Acc')
    plt.title('Accuracy History')
    plt.legend()
    
    plt.savefig('newmodel_training_history.png')
    print("Saved newmodel_training_history.png")


def main():
    parser = argparse.ArgumentParser(description='Train CNN for Cattle Breed Classification')
    parser.add_argument('--data_dir', type=str, default="/home/punith/antigravity/hemanth-prj/data/cattle", help='Path to dataset')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    
    args = parser.parse_args()

    data_dir = args.data_dir
    batch_size = args.batch_size
    num_epochs = args.epochs
    num_classes = 50

    # 3. DATA AUGMENTATION
    data_transforms = {
        'train': transforms.Compose([
            transforms.RandomResizedCrop(224, scale=(0.7, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomAffine(degrees=30, translate=(0.2, 0.2), scale=(0.8, 1.2)),
            transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            transforms.RandomErasing(p=0.2, scale=(0.02, 0.2)) # Helps prevent overfitting on highly sampled minority classes
        ]),
        'val': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    print("Loading dataset...")
    full_dataset = datasets.ImageFolder(data_dir)
    class_names = full_dataset.classes
    
    dataset_len = len(full_dataset)
    targets = full_dataset.targets
    
    # Train/Val split ensuring class distribution is maintained
    train_idx, val_idx = train_test_split(list(range(dataset_len)), test_size=0.2, random_state=42, stratify=targets)
    
    train_targets = [targets[i] for i in train_idx]
    
    # 5. DEBUGGING & ANALYSIS: Print class distribution
    print(f"\n[Dataset Class Distribution]")
    train_counts = Counter(train_targets)
    for i, name in enumerate(class_names):
        print(f"{name}: {train_counts[i]} images")
        
    print(f"\nTotal Dataset: {dataset_len} | Train Set: {len(train_idx)} | Val Set: {len(val_idx)}")
    
    # 2. HANDLE CLASS IMBALANCE: compute_class_weight
    # We compute weights to use in the Sampler, but we will NOT pass them to CrossEntropyLoss
    # because using both a WeightedRandomSampler AND weighted Loss applies the weights twice!
    print("\nComputing class weights for Sampler...")
    classes = np.unique(train_targets)
    weights = compute_class_weight(class_weight='balanced', classes=classes, y=train_targets)
    
    # 2. HANDLE CLASS IMBALANCE: WeightedRandomSampler
    # Assign weight to each sample based on its class
    sample_weights = [weights[t] for t in train_targets]
    sampler = WeightedRandomSampler(weights=sample_weights, num_samples=len(sample_weights), replacement=True)

    # Subsets
    train_dataset = Subset(full_dataset, train_idx)
    val_dataset = Subset(full_dataset, val_idx)
    
    # Apply transforms
    class TransformedSubset(torch.utils.data.Dataset):
        def __init__(self, subset, transform=None):
            self.subset = subset
            self.transform = transform
        def __getitem__(self, index):
            x, y = self.subset[index]
            if self.transform: x = self.transform(x)
            return x, y
        def __len__(self):
            return len(self.subset)

    train_transformed = TransformedSubset(train_dataset, data_transforms['train'])
    val_transformed = TransformedSubset(val_dataset, data_transforms['val'])

    # Dataloaders (Note: shuffle must be False when using a sampler)
    dataloaders = {
        'train': DataLoader(train_transformed, batch_size=batch_size, sampler=sampler, num_workers=4),
        'val': DataLoader(val_transformed, batch_size=batch_size, shuffle=False, num_workers=4)
    }

    dataset_sizes = {'train': len(train_idx), 'val': len(val_idx)}
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\nUsing device: {device}\n")

    # 1. MODEL IMPROVEMENT: Transfer learning model (ResNet50)
    print("Initializing ResNet50 model pretrained on ImageNet...")
    model_ft = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
    
    # Freeze early layers (Layers 1 and 2 frozen, Layer 3 and 4 fine-tuned)
    for name, param in model_ft.named_parameters():
        if "layer1" in name or "layer2" in name or "conv1" in name or "bn1" in name:
            param.requires_grad = False
    
    # Modify final layer for 50 classes with dropout
    num_ftrs = model_ft.fc.in_features
    model_ft.fc = nn.Sequential(
        nn.Dropout(0.5), # Regularization
        nn.Linear(num_ftrs, num_classes)
    )

    model_ft = model_ft.to(device)

    # 2. HANDLE CLASS IMBALANCE & NOISE: CrossEntropyLoss with Label Smoothing
    # We removed weight=class_weights because WeightedRandomSampler already balances the batches!
    # Applying label_smoothing=0.1 helps normalize confident misclassifications on noisy scrape-data.
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    
    # Optimizer (Only optimize parameters that require grad)
    optimizer_ft = optim.Adam(filter(lambda p: p.requires_grad, model_ft.parameters()), lr=args.lr, weight_decay=1e-4)
    
    # 4. TRAINING IMPROVEMENTS: Learning Rate Scheduler (ReduceLROnPlateau based on Validation Loss)
    exp_lr_scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer_ft, mode='min', factor=0.5, patience=3, verbose=True)

    # Train model
    print("Starting Training Pipeline...")
    model_path = '/home/punith/antigravity/hemanth-prj/model/newmodel.pth'
    model_ft, history = train_model(model_ft, criterion, optimizer_ft, exp_lr_scheduler, 
                                    dataloaders, dataset_sizes, device, num_epochs=num_epochs, model_path=model_path)

    # Save training history plot
    plot_history(history)
    
    # Evaluate & Analysis
    evaluate_and_analyze(model_ft, dataloaders['val'], device, class_names)
    
    print("\nPipeline complete. You can run training or check logs.")

if __name__ == "__main__":
    main()
