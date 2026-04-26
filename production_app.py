import os
from flask import Flask, request, jsonify, send_from_directory, send_file
import pandas as pd
import joblib
import json
import numpy as np
from fpdf import FPDF
import io
import shap
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

app = Flask(__name__, static_folder='.', static_url_path='')

# --- SECURITY LAYER 1: Secure Headers ---
# Force HTTPS and set Content Security Policy
# Note: For local testing, you might need to disable force_https
Talisman(app, force_https=False) 

# --- SECURITY LAYER 2: Rate Limiting ---
# Prevents hackers from brute-forcing the API
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Load model and preprocessor
best_model_type = "Unknown"
model = None
preprocessor = None
explainer = None

def load_models():
    global model, preprocessor, best_model_type, explainer
    try:
        if os.path.exists('best_model.txt'):
            with open('best_model.txt', 'r') as f:
                best_model_type = f.read().strip()
        
        if best_model_type == "Neural Network":
            from tensorflow.keras.models import load_model
            model = load_model("osteoporosis_nn_model.h5")
            preprocessor = joblib.load("preprocessor.pkl")
        else:
            model = joblib.load('osteoporosis_best.pkl' if os.path.exists('osteoporosis_best.pkl') else 'osteoporosis.pkl')
        
        if best_model_type == "XGBoost":
            if hasattr(model, 'named_steps'):
                explainer = shap.TreeExplainer(model.named_steps['clf'])
            else:
                explainer = shap.TreeExplainer(model)
        
        print(f"Production Model Loaded: {best_model_type}")
    except Exception as e:
        print(f"Critical Error Loading Models: {e}")

load_models()

REQUIRED_FEATURES = [
    'Age', 'Gender', 'Hormonal Changes', 'Family History', 'Race/Ethnicity',
    'Body Weight', 'Calcium Intake', 'Vitamin D Intake', 'Physical Activity',
    'Smoking', 'Alcohol Consumption', 'Medical Conditions', 'Medications',
    'Prior Fractures'
]

@app.route('/')
def index():
    return serve_static('dashboard.html')

@app.route('/<path:path>')
def serve_static(path):
    # Only allow safe static files
    safe_extensions = ('.html', '.js', '.css', '.png', '.jpg', '.svg', '.json', '.pdf')
    if not path.endswith(safe_extensions):
        return "Access Denied", 403
    return send_from_directory('.', path)

@app.route('/api/predict', methods=['POST'])
@limiter.limit("5 per minute") # Extra strict limit for prediction API
def predict():
    if not model:
        return jsonify({'error': 'System maintenance in progress'}), 503
        
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    # Sanitize and validate inputs
    feature_dict = {}
    for feature in REQUIRED_FEATURES:
        val = data.get(feature, "Unknown")
        # Basic type checking
        if feature == 'Age':
            try: val = int(val)
            except: val = 50
        feature_dict[feature] = str(val)

    df = pd.DataFrame([feature_dict])

    # Add Age_Group
    bins = [0, 30, 45, 60, 75, 120]
    labels = ["Young Adult", "Adult", "Middle-Aged", "Senior", "Elderly"]
    df["Age_Group"] = pd.cut(df["Age"].astype(int), bins=bins, labels=labels, right=False).astype(str)

    try:
        if best_model_type == "Neural Network":
            X_proc = preprocessor.transform(df)
            probability = float(model.predict(X_proc, verbose=0)[0][0])
        else:
            probability = model.predict_proba(df)[0][1]

        return jsonify({
            'risk_score': round(float(probability) * 100, 2),
            'high_risk': bool(probability > 0.5),
            'model_used': best_model_type,
            'top_factors': get_shap_explanations(df)
        })
    except Exception as e:
        return jsonify({'error': 'Analysis error. Please verify input data.'}), 500

def get_shap_explanations(df):
    if not explainer or best_model_type != "XGBoost":
        return []
    try:
        if hasattr(model, 'named_steps'):
            proc_df = model.named_steps['pre'].transform(df)
            shap_output = explainer.shap_values(proc_df)
            feature_names = model.named_steps['pre'].get_feature_names_out()
        else:
            shap_output = explainer.shap_values(df)
            feature_names = df.columns
            
        values = shap_output[1][0] if isinstance(shap_output, list) else shap_output[0]
        contributions = []
        for i in range(len(feature_names)):
            name = feature_names[i].split("__")[-1].replace("_", " ").title()
            if values[i] > 0:
                contributions.append({'factor': name, 'impact': float(values[i])})
        
        return sorted(contributions, key=lambda x: x['impact'], reverse=True)[:3]
    except:
        return []

if __name__ == '__main__':
    # --- PRODUCTION SERVER ---
    # Using Waitress for Windows compatibility
    from waitress import serve
    print("Starting Production Server on http://0.0.0.0:8080")
    serve(app, host='0.0.0.0', port=8080)
