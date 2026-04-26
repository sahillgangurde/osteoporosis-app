import json

with open('osteoporosis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

code_str = """# =========================================================
# ENSEMBLE MODEL: XGBoost + SVM + Neural Network (MLP)
# =========================================================
from sklearn.ensemble import VotingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, roc_curve, auc
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

print("Initializing base models for Ensemble...")

# 1. XGBoost
xgb_clf = XGBClassifier(
    eval_metric='logloss', random_state=42, n_jobs=-1,
    n_estimators=300, max_depth=5, learning_rate=0.1, subsample=0.8
)

# 2. Support Vector Machine
# Note: probability=True is required for soft voting
svm_clf = SVC(kernel='rbf', C=1.0, probability=True, random_state=42)

# 3. Neural Network (Multi-Layer Perceptron)
# We use MLPClassifier here as it is natively supported by sklearn's VotingClassifier
mlp_clf = MLPClassifier(hidden_layer_sizes=(32, 32, 16), max_iter=500, random_state=42, early_stopping=True)

# Create the Ensemble Voting Classifier (Soft Voting for probability averaging)
ensemble_clf = VotingClassifier(
    estimators=[
        ('xgb', xgb_clf),
        ('svm', svm_clf),
        ('mlp', mlp_clf)
    ],
    voting='soft'
)

# Create the Pipeline with Preprocessing and SMOTE
# Assume preprocessor and SMOTE are already defined earlier in the notebook
ensemble_pipeline = ImbPipeline([
    ('preprocessor', preprocessor),
    ('smote', SMOTE(random_state=42, k_neighbors=5)),
    ('classifier', ensemble_clf)
])

print("Training the Ensemble Model (this may take a few minutes)...")
ensemble_pipeline.fit(X_train, y_train)
print("Training complete!\\n")

# Make predictions
y_pred_ens = ensemble_pipeline.predict(X_test)
y_prob_ens = ensemble_pipeline.predict_proba(X_test)[:, 1]

# Evaluate the model
print("--- Ensemble Classification Report ---")
print(classification_report(y_test, y_pred_ens))
print(f"Ensemble Accuracy: {accuracy_score(y_test, y_pred_ens):.4f}\\n")

# Visualizations (Confusion Matrix & ROC Curve)
fig, ax = plt.subplots(1, 2, figsize=(16, 6))

# Subplot 1: Confusion Matrix
cm_ens = confusion_matrix(y_test, y_pred_ens)
sns.heatmap(cm_ens, annot=True, fmt='d', cmap='Oranges', ax=ax[0])
ax[0].set_title('Ensemble Confusion Matrix', fontsize=14, fontweight='bold')
ax[0].set_xlabel('Predicted Label', fontsize=12)
ax[0].set_ylabel('True Label', fontsize=12)
ax[0].set_xticklabels(['Low Risk (0)', 'High Risk (1)'])
ax[0].set_yticklabels(['Low Risk (0)', 'High Risk (1)'])

# Subplot 2: ROC Curve
fpr, tpr, thresholds = roc_curve(y_test, y_prob_ens)
roc_auc = auc(fpr, tpr)
ax[1].plot(fpr, tpr, color='#FFA500', lw=2, label=f'Ensemble ROC curve (AUC = {roc_auc:.2f})')
ax[1].plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')
ax[1].set_xlim([0.0, 1.0])
ax[1].set_ylim([0.0, 1.05])
ax[1].set_xlabel('False Positive Rate', fontsize=12)
ax[1].set_ylabel('True Positive Rate', fontsize=12)
ax[1].set_title('Ensemble Receiver Operating Characteristic (ROC)', fontsize=14, fontweight='bold')
ax[1].legend(loc="lower right", fontsize=12)

plt.tight_layout()
plt.show()

# Save the model so the Flask app can use it
joblib.dump(ensemble_pipeline, 'osteoporosis.pkl')
print('Saved ensemble model as osteoporosis.pkl')
"""

new_cell = {
    "cell_type": "code",
    "execution_count": None,
    "id": "ensemble_model_cell_001",
    "metadata": {},
    "outputs": [],
    "source": [line + "\n" if i < len(code_str.split("\n")) - 1 else line for i, line in enumerate(code_str.split("\n"))]
}
nb['cells'].append(new_cell)

with open('osteoporosis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Appended ensemble model code to osteoporosis.ipynb successfully.")
