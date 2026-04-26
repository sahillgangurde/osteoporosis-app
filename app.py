import os
from flask import Flask, request, jsonify, send_from_directory, send_file
import pandas as pd
import joblib
import json
import numpy as np
from fpdf import FPDF
import io
import shap

app = Flask(__name__, static_folder='.', static_url_path='')

# Load model and preprocessor
best_model_type = "Unknown"
model = None
preprocessor = None
explainer = None

def load_models():
    global model, preprocessor, best_model_type
    try:
        if os.path.exists('best_model.txt'):
            with open('best_model.txt', 'r') as f:
                best_model_type = f.read().strip()
        
        print(f"Loading best model type: {best_model_type}")

        if best_model_type == "Neural Network":
            from tensorflow.keras.models import load_model
            model = load_model("osteoporosis_nn_model.h5")
            preprocessor = joblib.load("preprocessor.pkl")
        else:
            if os.path.exists('osteoporosis_best.pkl'):
                model = joblib.load('osteoporosis_best.pkl')
            else:
                model = joblib.load('osteoporosis.pkl')
            
        print("Models/Pipeline loaded successfully.")
        
        # Initialize SHAP explainer for XGBoost (if it's the best model)
        if best_model_type == "XGBoost":
            # For XGBoost, TreeExplainer is efficient
            # If model is a pipeline, we might need the internal classifier
            if hasattr(model, 'named_steps'):
                explainer = shap.TreeExplainer(model.named_steps['clf'])
            else:
                explainer = shap.TreeExplainer(model)
        elif best_model_type == "SVM":
            # SVM needs KernelExplainer (slower, using a sample as background)
            # We'll skip complex SHAP for SVM for now or use a simple version
            explainer = None
    except Exception as e:
        print(f"Error loading model: {e}")
        try:
            model = joblib.load('osteoporosis.pkl')
            print("Fallback to osteoporosis.pkl successful.")
        except:
            model = None

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
    if path.endswith('.html'):
        full_path = os.path.join('.', path)
        if not os.path.exists(full_path):
             return f"Page {path} not found", 404
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'app.js' not in content:
                content = content.replace("</body>", '<script src="/app.js"></script>\n</body>')
            return content
    return send_from_directory('.', path)

def _default_value_for(feature_name):
    defaults = {
        'Age': 50, 'Gender': 'Female', 'Hormonal Changes': 'Normal',
        'Family History': 'No', 'Race/Ethnicity': 'Caucasian', 'Body Weight': 'Normal',
        'Calcium Intake': 'Adequate', 'Vitamin D Intake': 'Sufficient',
        'Physical Activity': 'Active', 'Smoking': 'No', 'Alcohol Consumption': 'Unknown',
        'Medical Conditions': 'Unknown', 'Medications': 'Unknown', 'Prior Fractures': 'No'
    }
    return defaults.get(feature_name, 'Unknown')

@app.route('/api/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({'error': 'Model not loaded'}), 500
        
    data = request.json
    if not data:
        return jsonify({'error': 'No JSON payload provided'}), 400

    feature_dict = {}
    # Columns the model was trained with 'Unknown' as a valid category
    UNKNOWN_SAFE_COLS = {'Alcohol Consumption', 'Medical Conditions', 'Medications'}
    for feature in REQUIRED_FEATURES:
        val = data.get(feature, _default_value_for(feature))
        if val in [None, "None", "not_provided", "", "Unknown"]:
            if feature in UNKNOWN_SAFE_COLS:
                val = "Unknown"   # these columns have 'Unknown' as a trained category
            else:
                val = _default_value_for(feature)  # use safe clinical default
        feature_dict[feature] = val

    df = pd.DataFrame([feature_dict])

    # Add Age_Group — model was trained with this feature (improved_osteoporosis_ml.py)
    if 'Age' in df.columns:
        bins = [0, 30, 45, 60, 75, 120]
        labels = ["Young Adult", "Adult", "Middle-Aged", "Senior", "Elderly"]
        df["Age_Group"] = pd.cut(df["Age"], bins=bins, labels=labels, right=False).astype(str)

    # Sanitize: ensure no Categorical dtype reaches the sklearn encoder
    for col in df.columns:
        if hasattr(df[col], 'cat') or df[col].dtype == object:
            df[col] = df[col].astype(str)

    try:
        if best_model_type == "Neural Network":
            X_proc = preprocessor.transform(df)
            probability = float(model.predict(X_proc)[0][0])
        else:
            if hasattr(model, 'predict_proba'):
                probability = model.predict_proba(df)[0][1]
            else:
                probability = float(model.predict(df)[0])

        return jsonify({
            'risk_score': round(float(probability) * 100, 2),
            'high_risk': bool(probability > 0.5),
            'model_used': best_model_type,
            'top_factors': get_shap_explanations(df)
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def get_shap_explanations(df):
    global explainer, model
    if not explainer or best_model_type != "XGBoost":
        return []
        
    try:
        # Get SHAP values for this specific input
        if hasattr(model, 'named_steps'):
            proc_df = model.named_steps['pre'].transform(df)
            shap_output = explainer.shap_values(proc_df)
            feature_names = model.named_steps['pre'].get_feature_names_out()
        else:
            shap_output = explainer.shap_values(df)
            feature_names = df.columns
            
        # Binary classification handling: SHAP may return a list [class0, class1] or a single array
        if isinstance(shap_output, list):
            # For binary classification, we want impact on class 1 (High Risk)
            values = shap_output[1][0] if len(shap_output) > 1 else shap_output[0][0]
        else:
            values = shap_output[0]
            
        # Create list of (feature, value)
        contributions = []
        for i in range(len(feature_names)):
            # Clean up feature name (remove 'cat__', 'num__', and handle 'Age_Group_...')
            raw_name = feature_names[i]
            clean_name = raw_name.split("__")[-1].replace("_", " ").title()
            
            # If it's a one-hot encoded feature like "Gender_Female", simplify it to "Gender"
            if " " in clean_name:
                clean_name = clean_name.split(" ")[0]

            if values[i] > 0: # Only factors increasing risk
                contributions.append({'factor': clean_name, 'impact': float(values[i])})
                
        # Sort by impact and take top 3 unique factors
        unique_factors = {}
        for c in contributions:
            # Group common medical markers
            name = c['factor']
            if "Fracture" in name: name = "Prior Fractures"
            if "Condition" in name: name = "Medical History"
            if "Medication" in name: name = "Medication Load"
            
            if name not in unique_factors or c['impact'] > unique_factors[name]:
                unique_factors[name] = c['impact']
        
        sorted_factors = sorted(unique_factors.items(), key=lambda x: x[1], reverse=True)
        # Limit to top 3 for UI clarity
        return [{'factor': name, 'impact': val} for name, val in sorted_factors[:3]]
    except Exception as e:
        print(f"SHAP error: {e}")
        return []

@app.route('/api/download-report', methods=['POST'])
def download_report():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Osteoporosis Risk Clinical Report", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Patient Name: {data.get('Name', 'N/A')}", ln=True)
    pdf.cell(200, 10, txt=f"Age: {data.get('Age', 'N/A')}", ln=True)
    pdf.cell(200, 10, txt=f"Gender: {data.get('Gender', 'N/A')}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"Risk Assessment Result: {data.get('risk_score', '0')}%", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=f"Analysis: Based on the provided clinical data, your calculated risk of osteoporosis is {data.get('risk_score', '0')}%. This prediction was generated using an {data.get('model_used', 'AI')} model.")
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Input Data Summary:", ln=True)
    pdf.set_font("Arial", size=10)
    
    for key, value in data.items():
        if key not in ['Name', 'Age', 'Gender', 'risk_score', 'model_used', 'high_risk', 'explanation']:
            pdf.cell(200, 8, txt=f"{key}: {value}", ln=True)

    # Save PDF to buffer
    pdf_buffer = io.BytesIO()
    pdf_output = pdf.output(dest='S')
    if isinstance(pdf_output, str):
        pdf_buffer.write(pdf_output.encode('latin-1'))
    else:
        pdf_buffer.write(pdf_output)
    pdf_buffer.seek(0)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name='Osteoporosis_Report.pdf',
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)