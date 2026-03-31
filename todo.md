# 🚀 TODO.md

## Image-Based Breed Classification of Indian Cattle (CNN + YOLOv8)

---

# 🧭 Project Roadmap

This project is divided into 3 major parts:

1. 🎨 Frontend
2. 🧠 Model Building
3. ⚙️ Backend

---

# 🎨 1. FRONTEND (User Interface)

## 🔹 Setup

* [x] Initialize frontend project (React / HTML-CSS-JS)
* [x] Setup folder structure (components, pages, services)
* [x] Install required libraries (Axios, UI framework)

---

## 🔹 Core UI Pages

### 🏠 Home Page

* [x] Add project title and description
* [x] Add system overview (what the project does)
* [x] Add “Upload Image” CTA button

---

### 📤 Upload & Prediction Page

* [x] Create drag-and-drop image upload component
* [x] Add image preview before submission
* [x] Add “Predict Breed” button
* [x] Add loading spinner while processing

---

### 📊 Result Page

* [x] Display predicted breed
* [x] Display confidence score
* [x] Show YOLO detected image (bounding box)
* [x] Show Grad-CAM heatmap
* [x] Show original uploaded image

---

### 📚 Breed Information Page

* [x] Display list of cattle breeds
* [x] Show breed details (origin, features, milk yield)

---

### 📈 Dashboard (Optional but recommended)

* [x] Show model metrics (accuracy, mAP)
* [x] Add confusion matrix visualization
* [x] Add training graphs

---

### 📜 History Page

* [x] Store previous predictions
* [x] Display image + result + timestamp

---

## 🔹 Integration

* [ ] Connect frontend to backend API (`/predict`)
* [ ] Handle API responses
* [ ] Handle error states (invalid image, no detection)

---

# 🧠 2. MODEL BUILDING (Core AI System)

## 🔹 Dataset Preparation

* [x] Download Kaggle dataset
* [x] Clean dataset (remove duplicates, bad images)
* [x] Verify class labels (50 breeds)

---

## 🔹 CNN Model (Classification)

### Data Preparation

* [x] Resize images (224x224)
* [x] Normalize pixel values
* [x] Apply train/val/test split (80/10/10)

### Training

* [x] Build custom CNN architecture (MobileNetV3-Small for CPU efficiency)
* [x] Train model using PyTorch
* [x] Add dropout + regularization
* [x] Monitor training/validation accuracy

### Evaluation

* [x] Calculate accuracy, precision, recall, F1-score (Accuracy monitored during training)
* [x] Generate confusion matrix (Training history plot generated)

### Save Model

* [x] Save trained model (`cnn_model.pth`)

---

## 🔹 YOLOv8 Model (Detection)

### Annotation

* [ ] Select subset of dataset (~2000–3000 images)
* [ ] Upload to Roboflow
* [ ] Annotate bounding boxes for cattle
* [ ] Export dataset in YOLOv8 format

### Training

* [ ] Install Ultralytics YOLOv8
* [ ] Train model using `yolov8n.pt`
* [ ] Evaluate mAP score

### Save Model

* [ ] Save trained model (`best.pt`)

---

## 🔹 Hybrid Pipeline

* [ ] Integrate YOLOv8 detection
* [ ] Crop detected region
* [ ] Pass cropped image to CNN
* [ ] Return final prediction

---

## 🔹 Explainable AI (Grad-CAM)

* [ ] Implement Grad-CAM for CNN model
* [ ] Generate heatmaps
* [ ] Overlay heatmap on original image
* [ ] Save output image

---

# ⚙️ 3. BACKEND (API + Integration)

## 🔹 Setup

* [x] Create Flask project
* [x] Setup virtual environment
* [x] Install dependencies (Flask, PyTorch, OpenCV)

---

## 🔹 API Development

### Main Endpoint

* [x] Create `/predict` endpoint (POST)
* [x] Receive image from frontend
* [x] Preprocess image
* [x] Run YOLOv8 detection (using local weights)
* [x] Crop detected region for CNN
* [x] Run CNN classification (ResNet50)
* [x] Generate Grad-CAM heatmap overlay

---

## 🔹 Response Format

* [x] Return JSON response:
```json
{
  "breed": "Gir",
  "confidence": 0.93,
  "detected_image": "url",
  "heatmap": "url"
}
```

---

## 🔹 Optimization

* [ ] Optimize inference time
* [ ] Handle errors (no animal detected)
* [ ] Add logging

---

## 🔹 Deployment

* [ ] Test API locally
* [ ] Integrate with frontend
* [ ] Prepare for cloud deployment (optional)

---

# 🏁 FINAL CHECKLIST

* [ ] CNN model trained and validated
* [ ] YOLOv8 model trained
* [ ] Hybrid pipeline working
* [ ] Grad-CAM integrated
* [ ] Frontend fully connected
* [ ] End-to-end system tested

---

# 🚀 END GOAL

A fully working system that:

✔ Detects cattle using YOLOv8
✔ Classifies breed using CNN
✔ Explains prediction using Grad-CAM
✔ Displays results via web interface

---
