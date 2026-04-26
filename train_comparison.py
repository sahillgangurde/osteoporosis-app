import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from xgboost import XGBClassifier
from sklearn.svm import SVC
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

# Force TensorFlow to use CPU if you want to avoid GPU issues in some environments
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

def load_and_preprocess_data(csv_path):
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Handle missing values as seen in previous notebooks
    df['Alcohol Consumption'] = df['Alcohol Consumption'].fillna('Unknown')
    df['Medical Conditions'] = df['Medical Conditions'].fillna('None')
    df['Medications'] = df['Medications'].fillna('None')
    
    X = df.drop(['Id', 'Osteoporosis'], axis=1)
    y = df['Osteoporosis']
    
    categorical_cols = [
        'Gender', 'Hormonal Changes', 'Family History', 'Race/Ethnicity',
        'Body Weight', 'Calcium Intake', 'Vitamin D Intake', 'Physical Activity',
        'Smoking', 'Alcohol Consumption', 'Medical Conditions', 'Medications',
        'Prior Fractures'
    ]
    numerical_cols = ['Age']
    
    preprocessor = ColumnTransformer([
        ('num', StandardScaler(), numerical_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols)
    ])
    
    return X, y, preprocessor

def train_xgboost(X_train, y_train, preprocessor):
    print("\nTraining XGBoost model...")
    pipeline = ImbPipeline([
        ('preprocessor', preprocessor),
        ('smote', SMOTE(random_state=42)),
        ('classifier', XGBClassifier(
            eval_metric='logloss',
            random_state=42,
            n_jobs=-1,
            n_estimators=300,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8
        ))
    ])
    pipeline.fit(X_train, y_train)
    return pipeline

def train_svm(X_train, y_train, preprocessor):
    print("\nTraining SVM model...")
    pipeline = ImbPipeline([
        ('preprocessor', preprocessor),
        ('smote', SMOTE(random_state=42)),
        ('classifier', SVC(kernel='rbf', C=1.0, probability=True, random_state=42))
    ])
    pipeline.fit(X_train, y_train)
    return pipeline

def train_neural_network(X_train, y_train, X_test, y_test, preprocessor):
    print("\nTraining Neural Network (Keras)...")
    
    # Transform data manually for NN
    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)
    
    # Apply SMOTE
    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X_train_proc, y_train)
    
    input_dim = X_res.shape[1]
    
    model = Sequential([
        # Input layer (14 neurons as requested, but input_shape depends on transformed data)
        Dense(14, input_dim=input_dim, activation='relu', name='Input_Layer'),
        
        # 5 Hidden layers (Decreasing structure)
        Dense(64, activation='relu', name='Hidden_Layer_1'),
        Dense(32, activation='relu', name='Hidden_Layer_2'),
        Dense(16, activation='relu', name='Hidden_Layer_3'),
        Dense(8, activation='relu', name='Hidden_Layer_4'),
        Dense(4, activation='relu', name='Hidden_Layer_5'),
        
        # Output layer
        Dense(1, activation='sigmoid', name='Output_Layer')
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    # Train for 100 epochs as requested
    model.fit(
        X_res, y_res, 
        epochs=100, 
        batch_size=32, 
        validation_split=0.2, 
        verbose=0 # Set to 0 to keep output clean, the script will show final results
    )
    
    return model, X_test_proc

def evaluate_model(name, model, X_test, y_test, is_keras=False):
    if is_keras:
        y_prob = model.predict(X_test)
        y_pred = (y_prob > 0.5).astype(int).flatten()
    else:
        y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    return {
        'Model': name,
        'Accuracy': acc,
        'Precision': prec,
        'Recall': rec,
        'F1-Score': f1
    }

def main():
    X, y, preprocessor = load_and_preprocess_data('osteoporosis.csv')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    
    # Train Models
    xgb_model = train_xgboost(X_train, y_train, preprocessor)
    svm_model = train_svm(X_train, y_train, preprocessor)
    nn_model, X_test_nn = train_neural_network(X_train, y_train, X_test, y_test, preprocessor)
    
    # Evaluate Models
    results = []
    results.append(evaluate_model('XGBoost', xgb_model, X_test, y_test))
    results.append(evaluate_model('SVM', svm_model, X_test, y_test))
    results.append(evaluate_model('Neural Network', nn_model, X_test_nn, y_test, is_keras=True))
    
    # Display Results
    results_df = pd.DataFrame(results)
    print("\n--- Model Comparison Table ---")
    print(results_df.to_string(index=False))
    
    # Identify Best Model
    best_row = results_df.loc[results_df['Accuracy'].idxmax()]
    best_name = best_row['Model']
    print(f"\nBest Performing Model based on Accuracy: {best_name}")
    
    # Save the best model and preprocessor
    joblib.dump(preprocessor, 'preprocessor.pkl')
    
    if best_name == 'XGBoost':
        joblib.dump(xgb_model, 'osteoporosis_best.pkl')
    elif best_name == 'SVM':
        joblib.dump(svm_model, 'osteoporosis_best.pkl')
    else:
        nn_model.save('osteoporosis_best.h5')
        
    print(f"Saved the best model ({best_name}) and preprocessor.pkl")

if __name__ == "__main__":
    main()
