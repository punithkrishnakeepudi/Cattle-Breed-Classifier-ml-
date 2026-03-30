# 🐄 Cattle Breed Classifier

> **AI-Powered Image-Based Breed Classification of Indian Cattle**  
> CNN (ResNet-50) + YOLOv8 · Grad-CAM XAI · React + Vite Frontend · Flask Backend

[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react)](https://reactjs.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=flat-square&logo=pytorch)](https://pytorch.org/)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=flat-square&logo=vite)](https://vitejs.dev/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![Accuracy](https://img.shields.io/badge/Model_Accuracy-80%25-00b894?style=flat-square)](#-model-performance)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Model Performance](#-model-performance)
- [UI Screenshots](#-ui-screenshots)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Design System](#-design-system)
- [Roadmap](#-roadmap)

---

## 🌿 Overview

The **Cattle Breed Classifier** is a full-stack AI application for identifying and classifying **50 Indian cattle breeds** from photographs. It combines:

- A **YOLOv8** object detector to locate cattle in an image
- A **CNN (ResNet-50)** classifier fine-tuned on ~8,500+ images to predict the breed with confidence scores
- A **Grad-CAM** explainability layer to visualize what the model "sees"
- A **React + Vite** SPA frontend with the "Digital Pasture" glassmorphism design system
- A **Flask** REST API backend exposing a `/predict` endpoint

---

## 📊 Model Performance

> Evaluated on ResNet-50 trained with transfer learning, class-weighted sampling, and label smoothing.

| Metric | Score |
|---|---|
| **Overall Accuracy** | **80.0%** |
| Macro Precision | 79% |
| Macro Recall | 79% |
| Macro F1-Score | 78% |
| Weighted F1 | 79% |
| Total Classes | 50 |
| Evaluation Samples | 1,715 |

### 🐄 All 50 Breeds — F1-Score (Highest → Lowest)

| # | Breed | F1-Score | Grade |
|---|---|---|---|
| 1 | Purnea | 98% | 🟢 Excellent |
| 2 | Bhelai | 98% | 🟢 Excellent |
| 3 | Kosali | 96% | 🟢 Excellent |
| 4 | Umblachery | 94% | 🟢 Excellent |
| 5 | Konkan Kapila | 93% | 🟢 Excellent |
| 6 | Siri | 93% | 🟢 Excellent |
| 7 | Poda Thirupu | 92% | 🟢 Excellent |
| 8 | Bargur | 91% | 🟢 Excellent |
| 9 | Dangi | 91% | 🟢 Excellent |
| 10 | Lakhimi | 91% | 🟢 Excellent |
| 11 | Ponwar | 91% | 🟢 Excellent |
| 12 | Ayrshire | 90% | 🟢 Excellent |
| 13 | Mewati | 89% | 🟢 Excellent |
| 14 | Ladakhi | 88% | 🟢 Excellent |
| 15 | Punganur | 88% | 🟢 Excellent |
| 16 | Malnad Gidda | 87% | 🟢 Excellent |
| 17 | Motu | 87% | 🟢 Excellent |
| 18 | Kenkatha | 85% | 🟢 Excellent |
| 19 | Khariar | 84% | 🟢 Excellent |
| 20 | Kangayam | 83% | 🟢 Excellent |
| 21 | Rathi | 83% | 🟢 Excellent |
| 22 | Vechur | 81% | 🟢 Excellent |
| 23 | Gir | 81% | 🟢 Excellent |
| 24 | Sahiwal | 81% | 🟢 Excellent |
| 25 | Badri | 81% | 🟢 Excellent |
| 26 | Himachali Pahari | 81% | 🟢 Excellent |
| 27 | Red Kandhari | 81% | 🟢 Excellent |
| 28 | Pulikulam | 80% | 🟢 Excellent |
| 29 | Thutho | 80% | 🟢 Excellent |
| 30 | Deoni | 78% | 🟡 Good |
| 31 | Nagori | 77% | 🟡 Good |
| 32 | Hariana | 77% | 🟡 Good |
| 33 | Nari | 76% | 🟡 Good |
| 34 | Nimari | 76% | 🟡 Good |
| 35 | Tharparkar | 74% | 🟡 Good |
| 36 | Kankrej | 74% | 🟡 Good |
| 37 | Ghumsari | 72% | 🟡 Good |
| 38 | Khillari | 72% | 🟡 Good |
| 39 | Bachaur | 71% | 🟡 Good |
| 40 | Hallikar | 69% | 🟡 Good |
| 41 | Dagri | 68% | 🟡 Good |
| 42 | Amritmahal | 67% | 🟡 Good |
| 43 | Gaolao | 67% | 🟡 Good |
| 44 | Kherigarh | 63% | 🟠 Fair |
| 45 | Ongole | 57% | 🟠 Fair |
| 46 | Shweta Kapila | 56% | 🟠 Fair |
| 47 | Krishna Valley | 54% | 🟠 Fair |
| 48 | Red Sindhi | 50% | 🔴 Needs Data |
| 49 | Malvi | 47% | 🔴 Needs Data |
| 50 | Gangatari | 36% | 🔴 Needs Data |

> **Breeds marked 🔴** have limited training data. Collecting more images for these classes is the primary next step for pushing accuracy above 85%.

---

## 📸 UI Screenshots

### 🏠 Home Page
Hero section with key stats, breed tags, feature cards, and a CTA button.

![Home Page](public/screenshots/ss_home.png)

---

### 📤 Upload & Classify Page
Drag-and-drop upload zone with image preview, 4-step pipeline sidebar, and animated progress bar.

![Upload Page](public/screenshots/ss_upload.png)

---

### 📊 Results Page
YOLO bounding-box visualization, Grad-CAM heatmap explainability, breed confidence breakdown, and quick-info panel.

![Results Page](public/screenshots/ss_result.png)

---

### 📚 Breed Library
Searchable grid of all 50 Indian cattle breeds with detailed information panel — origin, milk yield, physical characteristics, and conservation status.

![Breeds Page](public/screenshots/ss_breeds.png)

---

### 📈 Model Performance Dashboard
KPI cards (80% Accuracy, Precision, Recall, F1), training/validation accuracy SVG chart, all 50 breed F1-score bars (color-coded), and confusion matrix heatmap.

![Dashboard Page](public/screenshots/ss_dashboard.png)

---

### 📜 Prediction History
Searchable, sortable table of all past predictions with status badges, timestamps, and CSV export.

![History Page](public/screenshots/ss_history.png)

---

## ✨ Features

| Feature | Status |
|---|---|
| 🖼️ Image Upload (Drag & Drop + Browse) | ✅ Done |
| 🔍 YOLOv8 Cattle Detection | ✅ Done |
| 🤖 CNN Breed Classification (ResNet-50) | ✅ Done |
| 📊 Confidence Score Display | ✅ Done |
| 🌡️ Grad-CAM Heatmap Explainability | ✅ Done |
| 📚 Breed Library (50 breeds) | ✅ Done |
| 📈 Model Performance Dashboard (All 50 breeds) | ✅ Done |
| 📜 Prediction History Log | ✅ Done |
| ⬇️ Export CSV | ✅ Done |
| 📱 Responsive Design | ✅ Done |
| 🔗 Flask Backend API (`/predict`) | ✅ Done |

---

## 🛠️ Tech Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| **React** | 19.x | UI Framework |
| **React Router DOM** | 7.x | Client-side Routing |
| **Vite** | 5.x | Build Tool & Dev Server |
| **Vanilla CSS** | — | Styling (Design System) |
| **Google Fonts** | Manrope + Inter | Typography |

### Backend / ML
| Technology | Purpose |
|---|---|
| **Flask** | REST API (`/predict` endpoint) |
| **PyTorch 2.x** | CNN ResNet-50 model training & inference |
| **Torchvision** | Pre-trained weights & transforms |
| **Ultralytics YOLOv8** | Cattle object detection |
| **Grad-CAM** | Model explainability heatmaps |
| **scikit-learn** | Class weights, metrics, evaluation |
| **Python-venv** | Isolated dependency management |

---

## 🚀 Getting Started

### Prerequisites
- Node.js ≥ 18.x
- Python ≥ 3.10
- GPU recommended for model inference

### Frontend Setup

```bash
# Clone the repository
git clone https://github.com/punithkrishnakeepudi/Cattle-Breed-Classifier-ml-.git
cd Cattle-Breed-Classifier-ml-

# Install frontend dependencies
npm install

# Start development server
npm run dev
```

The app will be available at **http://localhost:5173**

### Backend Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
pip install torch torchvision flask flask-cors ultralytics scikit-learn matplotlib seaborn

# Start Flask API
python backend/app.py
```

Backend runs at **http://localhost:5000**

### Run Model Evaluation

```bash
source venv/bin/activate
python scripts/evaluate_model.py
# Generates: reports/newmodel_evaluation_cm.png + classification report
```

---

## 📁 Project Structure

```
hemanth-prj/
├── backend/
│   └── app.py                 # Flask API — /predict, /health, /gradcam
├── data/
│   └── cattle/                # 50 breed folders (~8,500 images)
├── models/
│   ├── newmodel.pth           # Trained ResNet-50 weights
│   └── best.pt                # YOLOv8 cattle detector weights
├── scripts/
│   ├── train_cnn.py           # Full training pipeline (ResNet-50)
│   ├── evaluate_model.py      # Evaluation + confusion matrix
│   ├── analyze_data.py        # Dataset distribution analysis
│   └── verify_data.py         # Dataset integrity check
├── reports/
│   └── newmodel_evaluation_cm.png  # Confusion matrix output
├── public/
│   ├── breeds/                # Breed reference images (50)
│   └── screenshots/           # UI preview screenshots
├── src/
│   ├── components/
│   │   ├── Navbar.jsx
│   │   └── Navbar.css
│   ├── data/
│   │   └── breeds.json        # 50 breed metadata (traits, milk, origin)
│   ├── pages/
│   │   ├── HomePage.jsx / .css
│   │   ├── UploadPage.jsx / .css
│   │   ├── ResultPage.jsx / .css
│   │   ├── BreedsPage.jsx / .css
│   │   ├── DashboardPage.jsx / .css
│   │   └── HistoryPage.jsx / .css
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css              # Global design system
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

---

## 🎨 Design System

The UI follows the **"Digital Pasture"** design language:

| Token | Value | Use |
|---|---|---|
| `--primary` | `#006b55` | Buttons, headings, key text |
| `--primary-container` | `#00b894` | Gradient end, chips |
| `--secondary-container` | `#78f9cc` | Confidence badges |
| `--surface` | `#e9ffeb` | Page background |
| Font Display | **Manrope** | Headings, nav |
| Font Body | **Inter** | Paragraphs, labels |
| Border Radius | `8px / 12px / 16px / 24px` | Progressive rounding |

Key principles:
- ✅ **Glassmorphism** — `backdrop-filter: blur(14px)` on all cards/nav
- ✅ **No hard borders** — only tonal background shifts
- ✅ **Ambient shadows** — `0 8px 40px rgba(0,33,14,0.10)`
- ✅ **Interactive glows** — `rgba(120,249,204,0.3)` on hover

---

## 🗺️ Roadmap

### ✅ Phase 1 — Frontend UI (Complete)
- [x] React + Vite project setup
- [x] Design system ("Digital Pasture" theme)
- [x] All 6 pages (Home, Upload, Result, Breeds, Dashboard, History)

### ✅ Phase 2 — Model Building (Complete)
- [x] Dataset: 50 Indian cattle breed classes (~8,500 images)
- [x] Transfer learning with ResNet-50 (ImageNet pre-trained)
- [x] Class imbalance handling (WeightedRandomSampler + Label Smoothing)
- [x] Strong data augmentation (RandomResizedCrop, Jitter, RandomErasing)
- [x] Early stopping + ReduceLROnPlateau scheduler
- [x] **Achieved 80% overall accuracy** (up from 35% baseline)
- [x] YOLOv8 cattle object detection

### ✅ Phase 3 — Backend & Integration (Complete)
- [x] Flask REST API (`/predict`, `/health`, `/gradcam`)
- [x] Frontend ↔ Backend integration
- [x] Grad-CAM heatmap generation

### 🔄 Phase 4 — Accuracy Improvement (Ongoing)
- [ ] Collect more images for 🔴 low-accuracy breeds (Gangatari, Malvi, Red Sindhi)
- [ ] Push accuracy target: **85%+**
- [ ] Cloud deployment (AWS / GCP / Render)

---

## 👥 Contributors

| Name | Role |
|---|---|
| **Hemanth** | ML Engineer, Project Lead |
| **Punith** | Frontend Developer |

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <p>Made with ❤️ for Indian Agriculture</p>
  <p>🐄 Classify · 🧠 Understand · 📊 Improve</p>
</div>
