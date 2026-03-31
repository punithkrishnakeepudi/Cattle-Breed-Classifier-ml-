import os
from collections import Counter
import torch
import numpy as np

def analyze_dataset(data_dir):
    classes = sorted(os.listdir(data_dir))
    counts = {}
    for cls in classes:
        cls_path = os.path.join(data_dir, cls)
        if os.path.isdir(cls_path):
            counts[cls] = len(os.listdir(cls_path))
    
    total = sum(counts.values())
    num_classes = len(counts)
    
    print(f"Total images: {total}")
    print(f"Number of classes: {num_classes}")
    print("\nClass Distribution (Top 5):")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for cls, count in sorted_counts[:5]:
        print(f"  {cls}: {count} ({count/total:.2%})")
        
    print("\nClass Distribution (Bottom 5):")
    for cls, count in sorted_counts[-5:]:
        print(f"  {cls}: {count} ({count/total:.2%})")
        
    # Compute class weights
    # weight = total / (num_classes * count)
    weights = [total / (num_classes * counts[cls]) for cls in classes]
    weights_tensor = torch.FloatTensor(weights)
    
    print("\nComputed Class Weights (Example):")
    for i, cls in enumerate(classes[:5]):
        print(f"  {cls}: {weights[i]:.4f}")
        
    return weights

if __name__ == "__main__":
    analyze_dataset('/home/punith/antigravity/hemanth-prj/data/cattle')
