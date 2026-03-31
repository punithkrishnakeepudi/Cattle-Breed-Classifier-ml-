import torch
import torch.nn as nn
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader, Subset
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.model_selection import train_test_split
import os

def evaluate_model_and_save_cm(model_name, model_path, data_dir, num_classes=50):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Evaluating model: {model_name} on device: {device}")

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
    try:
        model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    except Exception as e:
        print(f"Failed to load {model_name}: {e}")
        return 0.0

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

    accuracy = accuracy_score(all_labels, all_preds)
    print(f"Accuracy for {model_name}: {accuracy:.4f}")

    # Confusion Matrix (Save as image)
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(20, 20))
    sns.heatmap(cm, annot=False, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title(f'Confusion Matrix: {model_name}')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    output_img = f'/home/punith/antigravity/hemanth-prj/{model_name}_confusion_matrix.jpg'
    plt.savefig(output_img, format='jpg')
    print(f"Confusion matrix saved as {output_img}")
    plt.close()
    
    return accuracy

if __name__ == "__main__":
    data_dir = '/home/punith/antigravity/hemanth-prj/data/cattle'
    models_dir = '/home/punith/antigravity/hemanth-prj/model'
    model_files = ['cnn_model.pth', 'newmodel.pth']
    
    best_model = None
    best_acc = -1
    
    for model_file in model_files:
        path = os.path.join(models_dir, model_file)
        model_name = model_file.replace('.pth', '')
        if os.path.exists(path):
            acc = evaluate_model_and_save_cm(model_name, path, data_dir)
            if acc > best_acc:
                best_acc = acc
                best_model = model_name
        else:
            print(f"Model file {path} not found.")
            
    print(f"---")
    print(f"Best model is {best_model} with accuracy: {best_acc:.4f}")
