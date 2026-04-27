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
    global model, preprocessor, best_model_type, explainer
    try:
        if os.path.exists('best_model.txt'):
            with open('best_model.txt', 'r') as f:
                best_model_type = f.read().strip()
        
        print(f"Loading best model type: {best_model_type}")

        if best_model_type == "Neural Network":
            try:
                from tensorflow.keras.models import load_model
                model = load_model("osteoporosis_nn_model.h5")
                preprocessor = joblib.load("preprocessor.pkl")
            except ImportError:
                print("TensorFlow not installed. Falling back to XGBoost/PKL model.")
                best_model_type = "XGBoost"
                model = joblib.load('osteoporosis_best.pkl' if os.path.exists('osteoporosis_best.pkl') else 'osteoporosis.pkl')
        else:
            if os.path.exists('osteoporosis_best.pkl'):
                model = joblib.load('osteoporosis_best.pkl')
            else:
                model = joblib.load('osteoporosis.pkl')
            
        print("Models/Pipeline loaded successfully.")
        
        if best_model_type == "XGBoost" and model:
            try:
                if hasattr(model, 'named_steps'):
                    explainer = shap.TreeExplainer(model.named_steps['clf'])
                else:
                    explainer = shap.TreeExplainer(model)
            except:
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
    UNKNOWN_SAFE_COLS = {'Alcohol Consumption', 'Medical Conditions', 'Medications'}
    for feature in REQUIRED_FEATURES:
        val = data.get(feature, _default_value_for(feature))
        if val in [None, "None", "not_provided", "", "Unknown"]:
            if feature in UNKNOWN_SAFE_COLS:
                val = "Unknown"
            else:
                val = _default_value_for(feature)
        feature_dict[feature] = val
    df = pd.DataFrame([feature_dict])
    if 'Age' in df.columns:
        bins = [0, 30, 45, 60, 75, 120]
        labels = ["Young Adult", "Adult", "Middle-Aged", "Senior", "Elderly"]
        df["Age_Group"] = pd.cut(df["Age"], bins=bins, labels=labels, right=False).astype(str)
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
        return jsonify({'error': str(e)}), 500

def get_shap_explanations(df):
    global explainer, model
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
        if isinstance(shap_output, list):
            values = shap_output[1][0] if len(shap_output) > 1 else shap_output[0][0]
        else:
            values = shap_output[0]
        contributions = []
        for i in range(len(feature_names)):
            raw_name = feature_names[i]
            clean_name = raw_name.split("__")[-1].replace("_", " ").title()
            if " " in clean_name: clean_name = clean_name.split(" ")[0]
            if values[i] > 0:
                contributions.append({'factor': clean_name, 'impact': float(values[i])})
        unique_factors = {}
        for c in contributions:
            name = c['factor']
            if "Fracture" in name: name = "Prior Fractures"
            if "Condition" in name: name = "Medical History"
            if "Medication" in name: name = "Medication Load"
            if name not in unique_factors or c['impact'] > unique_factors[name]:
                unique_factors[name] = c['impact']
        sorted_factors = sorted(unique_factors.items(), key=lambda x: x[1], reverse=True)
        return [{'factor': name, 'impact': val} for name, val in sorted_factors[:3]]
    except:
        return []

def safe_str(val):
    """Sanitize string for FPDF latin-1 encoding."""
    if val is None: return "N/A"
    return str(val).encode('latin-1', 'replace').decode('latin-1')

@app.route('/api/download-report', methods=['POST'])
def download_report():
    data = request.json
    if not data: return jsonify({'error': 'No data provided'}), 400
    
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # --- Header ---
        pdf.set_fill_color(46, 2, 233) 
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 24)
        pdf.set_y(10)
        pdf.cell(0, 15, "OsteoScan AI", ln=True, align='C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 5, "Precision Bone Health Analysis - Clinical Suite", ln=True, align='C')
        
        # --- Confidential Label ---
        pdf.ln(20)
        pdf.set_text_color(186, 26, 26)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 10, "CONFIDENTIAL MEDICAL RECORD", ln=True, align='R')
        
        # --- Patient Information Box ---
        pdf.set_text_color(25, 28, 32)
        pdf.set_fill_color(242, 243, 249)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 12, "  Patient Profile", ln=True, fill=True)
        pdf.ln(2)
        
        pdf.set_font("Arial", '', 11)
        name = safe_str(data.get('Name', 'N/A'))
        age = safe_str(data.get('Age', 'N/A'))
        gender = safe_str(data.get('Gender', 'N/A'))
        ethnicity = safe_str(data.get('Race/Ethnicity', 'N/A'))
        
        pdf.cell(95, 10, f"  Name: {name}", border='B')
        pdf.cell(95, 10, f"  Age: {age}", border='B', ln=True)
        pdf.cell(95, 10, f"  Gender: {gender}", border='B')
        pdf.cell(95, 10, f"  Origin: {ethnicity}", border='B', ln=True)
        
        # --- Risk Assessment Section ---
        pdf.ln(10)
        pdf.set_fill_color(255, 218, 214)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 12, "  Risk Assessment Results", ln=True, fill=True)
        pdf.ln(5)
        
        risk_score = float(data.get('risk_score', 0))
        risk_level = "HIGH RISK" if risk_score > 50 else "MODERATE/LOW RISK"
        
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(186, 26, 26)
        pdf.cell(0, 15, f"Risk Score: {risk_score:.2f}%", ln=True, align='C')
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 5, f"Status: {risk_level}", ln=True, align='C')
        
        pdf.ln(10)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", '', 11)
        explanation = safe_str(data.get('explanation', 'Clinical markers analyzed using machine learning architecture.'))
        pdf.multi_cell(0, 7, txt=f"Analysis Summary: {explanation}", align='J')
        
        # --- Clinical Markers ---
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Clinical Data Points Summary:", ln=True)
        pdf.set_font("Arial", '', 10)
        
        items = [(k, v) for k, v in data.items() if k not in ['Name', 'Age', 'Gender', 'risk_score', 'model_used', 'high_risk', 'explanation', 'Race/Ethnicity', 'top_factors']]
        for i in range(0, len(items), 2):
            k1, v1 = items[i]
            line = safe_str(f"  • {k1}: {v1}")
            if i + 1 < len(items):
                k2, v2 = items[i+1]
                pdf.cell(95, 8, line)
                pdf.cell(95, 8, safe_str(f"  • {k2}: {v2}"), ln=True)
            else:
                pdf.cell(0, 8, line, ln=True)
        
        # --- Footer ---
        pdf.set_y(-40)
        pdf.set_font("Arial", 'I', 8)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 5, "This report is generated by AI and intended for clinical screening purposes only.", ln=True, align='C')
        pdf.cell(0, 5, "Generated via OsteoScan AI Clinical Suite. Verify with DEXA scan if score is > 50%.", ln=True, align='C')
        
        # Generate output string and convert to bytes safely
        pdf_str = pdf.output(dest='S')
        if isinstance(pdf_str, str):
            pdf_bytes = pdf_str.encode('latin-1')
        else:
            pdf_bytes = pdf_str
            
        return send_file(
            io.BytesIO(pdf_bytes),
            as_attachment=True,
            download_name=f'OsteoScan_Report.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'PDF Generation failed: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)