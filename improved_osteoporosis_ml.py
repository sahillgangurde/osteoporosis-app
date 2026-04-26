import os
import sys
import subprocess
import pandas as pd
import numpy as np
import joblib
import pickle
import warnings
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.svm import SVC
from xgboost import XGBClassifier
# Delaying imblearn imports to allow check_dependencies() to run first


# Silence warnings
warnings.filterwarnings("ignore")

# 1. Dependency Check
def check_dependencies():
    required = {"pandas", "numpy", "sklearn", "xgboost", "imblearn", "tensorflow", "joblib"}
    missing = []
    for lib in required:
        try:
            __import__(lib if lib != "sklearn" else "sklearn")
        except ImportError:
            missing.append(lib if lib != "imblearn" else "imbalanced-learn")
    
    if missing:
        print(f"Missing libraries: {missing}. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
    else:
        print("All required libraries are present.")

# 2. Data Loading & Advanced Preprocessing
def load_and_preprocess(filepath="osteoporosis.csv"):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at {filepath}")
        
    df = pd.read_csv(filepath)
    print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")

    # Drop ID
    df.drop(columns=["Id"], inplace=True, errors="ignore")

    # MANDATORY: Handle missing values properly
    # Alcohol Consumption, Medical Conditions, Medications have many NaNs
    cols_to_fill = ["Alcohol Consumption", "Medical Conditions", "Medications"]
    for col in cols_to_fill:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    # MANDATORY: Add Age_Group feature (binning)
    # Bins: <30, 30-45, 45-60, 60-75, >75
    bins = [0, 30, 45, 60, 75, 120]
    labels = ["Young Adult", "Adult", "Middle-Aged", "Senior", "Elderly"]
    df["Age_Group"] = pd.cut(df["Age"], bins=bins, labels=labels, right=False).astype(str)

    # Features and Target
    X = df.drop(columns=["Osteoporosis"])
    y = df["Osteoporosis"]

    return X, y

# 3. Pipeline Construction (Preprocessing + Scaling)
def get_preprocessor(X):
    categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    numerical_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()

    print(f"   Categorical features: {len(categorical_cols)}")
    print(f"   Numerical features: {numerical_cols}")

    # MANDATORY: Correct Encoding (OneHot) and Scaling (Standard)
    # Scaler for Age ensures it doesn't dominate based on scale alone
    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), numerical_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols)
    ])
    
    return preprocessor

# 4. Neural Network Builder (Moderated Depth)
def build_nn(input_dim):
    # Using TensorFlow inside the function to allow imports to happen globally or locally
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Dropout, BatchNormalization

    model = Sequential([
        # Hidden Layer 1
        Dense(64, input_dim=input_dim, activation="relu"),
        BatchNormalization(),
        Dropout(0.2),
        
        # Hidden Layer 2
        Dense(32, activation="relu"),
        BatchNormalization(),
        Dropout(0.2),
        
        # Hidden Layer 3
        Dense(16, activation="relu"),
        BatchNormalization(),
        
        # Output Layer
        Dense(1, activation="sigmoid")
    ])
    
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model

# 5. Training Logic with Cross-Validation
def train_and_evaluate_models(X_train, X_test, y_train, y_test, preprocessor):
    results = {}
    
    # K-Fold for Cross-Validation
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    # --- XGBoost ---
    print("\n  Training XGBoost (with CV)...")
    from imblearn.over_sampling import SMOTE
    from imblearn.pipeline import Pipeline as ImbPipeline

    xgb_pipe = ImbPipeline([
        ("pre", preprocessor),
        ("smote", SMOTE(random_state=42)),
        ("clf", XGBClassifier(eval_metric="logloss", n_estimators=100, random_state=42))
    ])
    
    # CV Scores
    cv_acc = cross_val_score(xgb_pipe, X_train, y_train, cv=kf, scoring="accuracy").mean()
    xgb_pipe.fit(X_train, y_train)
    
    # Test Predictions
    y_pred = xgb_pipe.predict(X_test)
    results["XGBoost"] = {
        "model": xgb_pipe,
        "acc": accuracy_score(y_test, y_pred),
        "cv_acc": cv_acc,
        "f1": f1_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred)
    }
    
    # Feature Importance for XGBoost (Bias Check)
    clf = xgb_pipe.named_steps["clf"]
    feature_names = preprocessor.get_feature_names_out()
    importances = clf.feature_importances_
    feat_imp = pd.Series(importances, index=feature_names).sort_values(ascending=False)
    print("   Top 5 Important Features for XGBoost:")
    print(feat_imp.head(5))

    # --- SVM ---
    print("\n  Training SVM (with CV)...")
    from imblearn.over_sampling import SMOTE
    from imblearn.pipeline import Pipeline as ImbPipeline
    
    svm_pipe = ImbPipeline([
        ("pre", preprocessor),
        ("smote", SMOTE(random_state=42)),
        ("clf", SVC(probability=True, kernel="rbf", random_state=42))
    ])
    
    cv_acc = cross_val_score(svm_pipe, X_train, y_train, cv=kf, scoring="accuracy").mean()
    svm_pipe.fit(X_train, y_train)
    
    y_pred = svm_pipe.predict(X_test)
    results["SVM"] = {
        "model": svm_pipe,
        "acc": accuracy_score(y_test, y_pred),
        "cv_acc": cv_acc,
        "f1": f1_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred)
    }

    # --- Neural Network ---
    print("\n  Training Neural Network...")
    import tensorflow as tf
    from tensorflow.keras.callbacks import EarlyStopping
    
    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)
    
    # SMOTE for NN
    from imblearn.over_sampling import SMOTE
    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X_train_proc, y_train)
    
    nn_model = build_nn(X_res.shape[1])
    early_stop = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)
    
    nn_model.fit(X_res, y_res, epochs=50, batch_size=32, validation_split=0.1, callbacks=[early_stop], verbose=0)
    
    y_prob = nn_model.predict(X_test_proc)
    y_pred = (y_prob > 0.5).astype(int).flatten()
    
    results["Neural Network"] = {
        "model": nn_model,
        "acc": accuracy_score(y_test, y_pred),
        "cv_acc": np.nan, # CV is computationally expensive for NN in this script
        "f1": f1_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred)
    }

    return results

# 6. Model Selection Improvement (Accuracy + F1 + Recall)
def select_best_model(results):
    print("\n" + "="*50)
    print("  MODEL COMPARISON (Accuracy, F1, Recall)")
    print("="*50)
    
    best_name = None
    best_score = -1
    
    for name, metrics in results.items():
        # Weighted Score: 40% Accuracy, 40% F1, 20% Recall
        score = (metrics["acc"] * 0.4) + (metrics["f1"] * 0.4) + (metrics["recall"] * 0.2)
        
        print(f"{name:15s} | Acc: {metrics['acc']:.4f} | F1: {metrics['f1']:.4f} | Recall: {metrics['recall']:.4f} | CV: {metrics['cv_acc']:.4f}")
        
        if score > best_score:
            best_score = score
            best_name = name
            
    print(f"\n  BEST MODEL: {best_name} (Selection Score: {best_score:.4f})")
    print("="*50)
    return best_name, results[best_name]["model"]

# 7. Bias Validation: Age Sensitivity Test
def verify_age_bias(model, preprocessor, sample_data, model_name):
    print(f"\n  Validating Bias (Age Sensitivity Test using {model_name})...")
    
    # Create copies of a single sample with varying ages
    test_ages = [25, 40, 55, 70, 85]
    synthetic_samples = []
    
    for age in test_ages:
        s = sample_data.copy()
        s["Age"] = age
        # Re-apply binning for the synthetic sample
        bins = [0, 30, 45, 60, 75, 120]
        labels = ["Young Adult", "Adult", "Middle-Aged", "Senior", "Elderly"]
        s["Age_Group"] = pd.cut([age], bins=bins, labels=labels, right=False)[0]
        synthetic_samples.append(s)
    
    test_df = pd.DataFrame(synthetic_samples)
    
    if model_name == "Neural Network":
        proc_data = preprocessor.transform(test_df)
        probs = model.predict(proc_data).flatten()
    else:
        # Standard pipeline for XGB/SVM handles internal preprocessing
        probs = model.predict_proba(test_df)[:, 1]
    
    print(f"   Age Analysis Results:")
    for age, prob in zip(test_ages, probs):
        print(f"   Age: {age} -> Prediction Probability: {prob:.4f}")
    
    # Check if predictions change but not exclusively based on age
    max_diff = max(probs) - min(probs)
    print(f"   Max probability delta across age spectrum: {max_diff:.4f}")
    if max_diff < 0.9:
        print("     Bias Check: Model shows sensitivity to age but isn't purely binary-coupled to it.")
    else:
        print("     Warning: High sensitivity to age detected.")

# MAIN EXECUTION
if __name__ == "__main__":
    check_dependencies()
    
    # Step 1: Data
    X, y = load_and_preprocess("osteoporosis.csv")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Step 2: Preprocessor
    preprocessor = get_preprocessor(X)
    
    # Step 3: Train
    results = train_and_evaluate_models(X_train, X_test, y_train, y_test, preprocessor)
    
    # Step 4: Select
    best_name, best_model = select_best_model(results)
    
    # Step 5: Save
    joblib.dump(preprocessor, "preprocessor.pkl")
    if best_name == "Neural Network":
        best_model.save("osteoporosis_nn_model.h5")
    else:
        joblib.dump(best_model, "osteoporosis_best.pkl")
    
    with open("best_model.txt", "w") as f:
        f.write(best_name)
    
    print("\nBest model and preprocessor saved successfully.")

    # Step 6: Age Sensitivity Validation (using a sample from test set)
    sample_patient = X_test.iloc[0].to_dict()
    verify_age_bias(best_model, preprocessor, sample_patient, best_name)
