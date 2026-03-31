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

## 🔹 Stitch Integration (UI Generation)

### 📌 Stitch Project Details

* Title: **Cattle Breed Classifier SPA**
* Project ID: `6679238663629048285`

### 📌 Screens

* Main Screen ID: `4faf37b9db914b2d863492838225750b`

---

### 📥 Download Stitch Assets

* [x] Use `curl` or browser to download assets

Example:

```bash
curl -L <stitch_image_url> -o image.png
curl -L <stitch_code_url> -o code.zip
```

* [x] Extract UI code and assets
* [x] Integrate into frontend project
* [x] Refactor components into reusable structure

---

### 🧠 Stitch Prompt (Frontend Generation Prompt)

Use this prompt inside Stitch MCP or UI generator:

Design a modern responsive web application UI for an AI-powered cattle breed classification system.

Project Name:
Cattle Breed Classifier SPA

Features:

* Image upload (drag-and-drop + camera)
* Breed prediction display
* Confidence score
* YOLO detection visualization (bounding boxes)
* Grad-CAM explainable AI heatmap
* Breed information panel
* Prediction history
* Model performance dashboard

Pages:

* Home page
* Upload & Predict page
* Result page
* Breed information page
* Dashboard page
* About page

Design:

* Clean, modern UI
* Agriculture-inspired theme (green, white)
* Mobile responsive
* Simple UX for farmers and researchers

---

## 🔹 Core UI Pages

### 🏠 Home Page

* [x] Add project title and description
* [x] Add system overview
* [x] Add “Upload Image” CTA button

---

### 📤 Upload & Prediction Page

* [x] Drag-and-drop image upload
* [x] Image preview
* [x] “Predict Breed” button
* [x] Loading spinner

---

### 📊 Result Page

* [x] Display predicted breed
* [x] Display confidence score
* [x] Show YOLO detection output
* [x] Show Grad-CAM heatmap
* [x] Show original image

---

### 📚 Breed Information Page

* [x] Show breed details
* [x] Add breed cards (image + info)

---

### 📈 Dashboard

* [x] Show accuracy, precision, recall
* [x] Add confusion matrix
* [x] Add training graphs

---

### 📜 History Page

* [x] Store previous predictions
* [x] Display results with timestamps

---

## 🔹 Integration

* [ ] Connect frontend to backend API (`/predict`)
* [ ] Handle API responses
* [ ] Handle errors

---

# 🧠 2. MODEL BUILDING (Core AI System)

## 🔹 Dataset Preparation

* [ ] Download Kaggle dataset
* [ ] Clean dataset (remove duplicates, bad images)
* [ ] Verify 50 breeds

---

## 🔹 CNN Model

* [ ] Resize images (224×224)
* [ ] Normalize dataset
* [ ] Train CNN (PyTorch)
* [ ] Add dropout & regularization
* [ ] Evaluate model
* [ ] Save model (`cnn_model.pth`)

---

## 🔹 YOLOv8 Model

* [ ] Select subset (2000–3000 images)
* [ ] Upload to Roboflow
* [ ] Annotate bounding boxes
* [ ] Export YOLOv8 dataset
* [ ] Train YOLOv8 model
* [ ] Save model (`best.pt`)
./venv/bin/python3 model_building/train_cnn.py --epochs 50 --subset 1.0

---

## 🔹 Hybrid Pipeline

* [ ] YOLO detect cattle
* [ ] Crop region
* [ ] CNN classify breed

---

## 🔹 Explainable AI

* [ ] Implement Grad-CAM
* [ ] Generate heatmaps
* [ ] Overlay on images

---

# ⚙️ 3. BACKEND (API + Integration)

## 🔹 Setup

* [ ] Setup Flask project
* [ ] Install dependencies

---

## 🔹 API

* [ ] Create `/predict` endpoint
* [ ] Accept image input
* [ ] Run full pipeline:

  * YOLO detection
  * Crop
  * CNN classification
  * Grad-CAM generation

---

## 🔹 Response Format

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

* [ ] Improve inference speed
* [ ] Handle errors

---

## 🔹 Deployment

* [ ] Test API locally
* [ ] Connect frontend
* [ ] Prepare for deployment

---

# 🏁 FINAL CHECKLIST

* [ ] CNN trained
* [ ] YOLOv8 trained
* [ ] Hybrid pipeline working
* [ ] Grad-CAM working
* [ ] Frontend connected
* [ ] End-to-end tested

---

# 🚀 FINAL GOAL

✔ Detect cattle
✔ Classify breed
✔ Explain prediction
✔ Display results in UI

---
