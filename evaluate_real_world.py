import pandas as pd
import numpy as np
import joblib
import os
import json
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    classification_report, confusion_matrix, roc_auc_score
)
from sklearn.model_selection import train_test_split

def load_best_model():
    best_model_type = "Unknown"
    if os.path.exists('best_model.txt'):
        with open('best_model.txt', 'r') as f:
            best_model_type = f.read().strip()
    
    print(f"--- Model Performance Evaluation ---")
    print(f"Target Model Type: {best_model_type}")

    if best_model_type == "Neural Network":
        from tensorflow.keras.models import load_model
        model = load_model("osteoporosis_nn_model.h5")
        preprocessor = joblib.load("preprocessor.pkl")
        return model, preprocessor, "NN"
    else:
        if os.path.exists('osteoporosis_best.pkl'):
            model = joblib.load('osteoporosis_best.pkl')
        else:
            model = joblib.load('osteoporosis.pkl')
        return model, None, "SK"

def run_evaluation():
    model, preprocessor, mtype = load_best_model()
    df = pd.read_csv('osteoporosis.csv')
    
    # Preprocessing as per training script
    df['Alcohol Consumption'] = df['Alcohol Consumption'].fillna('Unknown')
    df['Medical Conditions'] = df['Medical Conditions'].fillna('Unknown')
    df['Medications'] = df['Medications'].fillna('Unknown')
    
    # Add Age_Group if needed (some models expect it)
    bins = [0, 30, 45, 60, 75, 120]
    labels = ["Young Adult", "Adult", "Middle-Aged", "Senior", "Elderly"]
    df["Age_Group"] = pd.cut(df["Age"], bins=bins, labels=labels, right=False).astype(str)
    
    X = df.drop(['Id', 'Osteoporosis'], axis=1)
    y = df['Osteoporosis']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    
    print(f"\n[1] Evaluating on Real-World Test Subset ({len(X_test)} samples)")
    
    if mtype == "NN":
        X_test_proc = preprocessor.transform(X_test)
        y_prob = model.predict(X_test_proc, verbose=0)
        y_pred = (y_prob > 0.5).astype(int).flatten()
    else:
        y_pred = model.predict(X_test)
        if hasattr(model, 'predict_proba'):
            y_prob = model.predict_proba(X_test)[:, 1]
        else:
            y_prob = y_pred

    print("\nOverall Performance:")
    print(f"Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
    print(f"F1-Score:  {f1_score(y_test, y_pred):.4f}")
    print(f"Recall:    {recall_score(y_test, y_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred):.4f}")
    print(f"ROC-AUC:   {roc_auc_score(y_test, y_prob):.4f}")

    print("\n[2] Clinical Profile Stress Test")
    profiles = [
        {
            "Name": "High Risk Case",
            "Age": 82, "Gender": "Female", "Hormonal Changes": "Postmenopausal",
            "Family History": "Yes", "Race/Ethnicity": "Caucasian", "Body Weight": "Underweight",
            "Calcium Intake": "Low", "Vitamin D Intake": "Insufficient", "Physical Activity": "Sedentary",
            "Smoking": "Yes", "Alcohol Consumption": "Moderate", "Medical Conditions": "Rheumatoid Arthritis",
            "Medications": "Corticosteroids", "Prior Fractures": "Yes"
        },
        {
            "Name": "Low Risk Case",
            "Age": 25, "Gender": "Male", "Hormonal Changes": "Normal",
            "Family History": "No", "Race/Ethnicity": "African American", "Body Weight": "Normal",
            "Calcium Intake": "Adequate", "Vitamin D Intake": "Sufficient", "Physical Activity": "Active",
            "Smoking": "No", "Alcohol Consumption": "None", "Medical Conditions": "None",
            "Medications": "None", "Prior Fractures": "No"
        },
        {
            "Name": "Atypical (Middle-Aged Active)",
            "Age": 52, "Gender": "Female", "Hormonal Changes": "Normal",
            "Family History": "No", "Race/Ethnicity": "Asian", "Body Weight": "Normal",
            "Calcium Intake": "Adequate", "Vitamin D Intake": "Sufficient", "Physical Activity": "Active",
            "Smoking": "No", "Alcohol Consumption": "None", "Medical Conditions": "None",
            "Medications": "None", "Prior Fractures": "No"
        }
    ]

    for p in profiles:
        name = p.pop("Name")
        pdf = pd.DataFrame([p])
        # Add Age Group
        age = p['Age']
        pdf["Age_Group"] = pd.cut([age], bins=bins, labels=labels, right=False)[0]
        
        if mtype == "NN":
            p_proc = preprocessor.transform(pdf)
            prob = float(model.predict(p_proc, verbose=0)[0][0])
        else:
            prob = float(model.predict_proba(pdf)[0][1])
        
        print(f"Profile: {name:25s} | Risk Score: {prob*100:6.2f}% | {'HIGH RISK' if prob > 0.5 else 'LOW RISK'}")

    print("\n[3] Robustness Test (Unknown/Missing Inputs)")
    robust_p = profiles[1].copy()
    robust_p["Smoking"] = "Unknown"
    robust_p["Alcohol Consumption"] = "Not Provided"
    robust_p["Medical Conditions"] = "???"
    
    r_df = pd.DataFrame([robust_p])
    r_df["Age_Group"] = pd.cut([robust_p['Age']], bins=bins, labels=labels, right=False)[0]
    
    try:
        if mtype == "NN":
            r_proc = preprocessor.transform(r_df)
            prob = float(model.predict(r_proc, verbose=0)[0][0])
        else:
            prob = float(model.predict_proba(r_df)[0][1])
        print(f"Robustness: Handled unknown values successfully. Risk: {prob*100:.2f}%")
    except Exception as e:
        print(f"Robustness Warning: Model failed on unknown values: {e}")

if __name__ == "__main__":
    run_evaluation()
