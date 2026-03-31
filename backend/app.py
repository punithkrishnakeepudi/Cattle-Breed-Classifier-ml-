import os
import torch
import torch.nn as nn
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from torchvision import models, transforms
from PIL import Image
import numpy as np
import cv2
from ultralytics import YOLO
import time

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
UPLOAD_FOLDER = os.path.join(PARENT_DIR, 'static', 'uploads')
RESULT_FOLDER = os.path.join(PARENT_DIR, 'static', 'results')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

MODEL_PATH_CNN = os.path.join(PARENT_DIR, 'models', 'finetuned_v2.pth')
MODEL_PATH_YOLO = os.path.join(PARENT_DIR, 'models', 'best.pt')
NUM_CLASSES = 50

# List of breed names from data directory (alphabetical order)
CLASS_NAMES = [
    "Amritmahal", "Ayrshire", "Bargur", "Dangi", "Deoni", "Gir", "Hallikar", "Hariana", 
    "Himachali Pahari", "Kangayam", "Kankrej", "Kenkatha", "Khariar", "Khillari", 
    "Konkan Kapila", "Kosali", "Krishna_Valley", "Ladakhi", "Lakhimi", "Malnad_gidda", 
    "Mewati", "Nari", "Nimari", "Ongole", "Poda Thirupu", "Pulikulam", "Punganur", 
    "Purnea", "Rathi", "Red kandhari", "Red_Sindhi", "Sahiwal", "Shweta Kapila", 
    "Tharparkar", "Umblachery", "Vechur", "bachaur", "badri", "bhelai", "dagri", 
    "gangatari", "gaolao", "ghumsari", "kherigarh", "malvi", "motu", "nagori", 
    "ponwar", "siri", "thutho"
]

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Backend using device: {device}")

# --- MODEL LOADING ---
print("Loading YOLO model...")
yolo_model = YOLO(MODEL_PATH_YOLO)

print("Loading CNN model...")
def get_cnn_model():
    model = models.resnet50(weights=None)
    num_ftrs = model.fc.in_features
    # Matching architecture used in scripts/finetune_full.py
    model.fc = nn.Sequential(
        nn.BatchNorm1d(num_ftrs),
        nn.Dropout(0.5),
        nn.Linear(num_ftrs, 512),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(512, NUM_CLASSES)
    )
    model.load_state_dict(torch.load(MODEL_PATH_CNN, map_location=device, weights_only=True))
    model = model.to(device)
    model.eval()
    return model

cnn_model = get_cnn_model()

# --- PREPROCESSING ---
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# --- GRAD-CAM ---
class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self.hook_handle_fwd = target_layer.register_forward_hook(self.save_activations)
        self.hook_handle_bwd = target_layer.register_full_backward_hook(self.save_gradients)

    def save_activations(self, module, input, output):
        self.activations = output

    def save_gradients(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]

    def generate(self, input_tensor, class_idx=None):
        # Forward pass
        output = self.model(input_tensor)
        if class_idx is None:
            class_idx = torch.argmax(output)

        # Backward pass
        self.model.zero_grad()
        output[0, class_idx].backward()

        # Generate CAM
        weights = torch.mean(self.gradients, dim=(2, 3), keepdim=True)
        cam = torch.sum(weights * self.activations, dim=1).squeeze()
        cam = np.maximum(cam.detach().cpu().numpy(), 0)
        
        # Avoid division by zero if all zero
        if np.max(cam) != np.min(cam):
            cam = (cam - np.min(cam)) / (np.max(cam) - np.min(cam))
        
        cam = cv2.resize(cam, (224, 224))
        return cam

# ResNet50 target layer: last conv layer
grad_cam = GradCAM(cnn_model, cnn_model.layer4)

# --- UTILS ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_heatmap(image_path, cam, output_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (224, 224))
    heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
    result = cv2.addWeighted(img, 0.6, heatmap, 0.4, 0)
    cv2.imwrite(output_path, result)

# --- ENDPOINTS ---
@app.route('/', methods=['GET'])
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Cattle Breed Classifier API is running',
        'device': str(device),
        'models': {
            'cnn': 'ResNet-50 (loaded)',
            'yolo': 'YOLOv8 (loaded)'
        },
        'endpoints': {
            'POST /predict': 'Upload image, get breed prediction',
            'GET /health': 'API health check'
        }
    })

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image found'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{int(time.time())}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 1. DETECTION (YOLO)
        results = yolo_model(filepath)
        det_filename = f"det_{filename}"
        det_path = os.path.join(app.config['RESULT_FOLDER'], det_filename)
        
        # Save detection result to results folder
        res_plot = results[0].plot()
        cv2.imwrite(det_path, res_plot)

        # Hybrid Logic: Try to crop detection
        crop_filename = f"crop_{filename}"
        crop_path = os.path.join(app.config['RESULT_FOLDER'], crop_filename)
        found_animal = False
        active_img_path = filepath # Default to original

        if results[0].boxes is not None and len(results[0].boxes) > 0:
            # We crop the first detection (highest confidence)
            box = results[0].boxes[0].xyxy[0].cpu().numpy().astype(int)
            raw_img = cv2.imread(filepath)
            crop_img = raw_img[box[1]:box[3], box[0]:box[2]]
            if crop_img.size > 0:
                cv2.imwrite(crop_path, crop_img)
                active_img_path = crop_path
                found_animal = True

        # 2. CLASSIFICATION (CNN)
        img = Image.open(active_img_path).convert('RGB')
        input_tensor = preprocess(img).unsqueeze(0).to(device)
        
        # Note: Grad-CAM generate() will perform a forward and backward pass
        cam = grad_cam.generate(input_tensor)
        
        # Final prediction after backprop
        with torch.no_grad():
            outputs = cnn_model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, class_idx = torch.max(probabilities, 1)
            prediction = CLASS_NAMES[class_idx.item()]
            conf_score = confidence.item()

        # 3. GRAD-CAM HEATMAP
        heat_filename = f"heat_{filename}"
        heat_path = os.path.join(app.config['RESULT_FOLDER'], heat_filename)
        generate_heatmap(active_img_path, cam, heat_path)

        return jsonify({
            'breed': prediction,
            'confidence': round(conf_score, 4),
            'detected_image': f'/static/results/{det_filename}',
            'heatmap': f'/static/results/{heat_filename}',
            'original_image': f'/static/uploads/{filename}',
            'cropped_image': f'/static/results/{crop_filename}' if found_animal else None,
            'animal_detected': found_animal
        })

    return jsonify({'error': 'Invalid file extension'}), 400

# Static routes for development serving
@app.route('/static/uploads/<filename>')
def get_upload_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/static/results/<filename>')
def get_result_image(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
