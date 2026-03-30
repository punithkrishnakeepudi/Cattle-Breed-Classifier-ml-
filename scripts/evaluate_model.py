import torch
import torch.nn as nn
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader, Subset
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.model_selection import train_test_split
import os

import argparse

def evaluate_model(model_path, data_dir, num_classes=50):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Data transformation
    data_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # Load dataset
    full_dataset = datasets.ImageFolder(data_dir)
    class_names = full_dataset.classes
    
    # Train/Val split (same as training to ensure we test on unseen data)
    dataset_len = len(full_dataset)
    _, val_idx = train_test_split(list(range(dataset_len)), test_size=0.2, random_state=42)
    val_dataset = Subset(full_dataset, val_idx)
    
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

    val_transformed = TransformedSubset(val_dataset, data_transforms)
    dataloader = DataLoader(val_transformed, batch_size=32, shuffle=False, num_workers=4)

    # Initialize model
    model = models.resnet50(weights=None)
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(num_ftrs, num_classes)
    )
    
    # Load weights
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    model = model.to(device)
    model.eval()

    all_preds = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    # Metrics
    print("\nClassification Report:")
    report = classification_report(all_labels, all_preds, target_names=class_names, zero_division=0)
    print(report)

    # Confusion Matrix (Save as image)
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(20, 20))
    sns.heatmap(cm, annot=False, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.savefig('reports/newmodel_evaluation_cm.png')
    print("\nConfusion matrix saved as reports/newmodel_evaluation_cm.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluate a trained breed classifier')
    parser.add_argument('--model',    type=str, default='/home/punith/antigravity/hemanth-prj/models/newmodel.pth')
    parser.add_argument('--data_dir', type=str, default='/home/punith/antigravity/hemanth-prj/data/cattle')
    args = parser.parse_args()
    os.makedirs('reports', exist_ok=True)
    evaluate_model(args.model, args.data_dir)
