import numpy as np
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib

# 路径配置
FEATURE_PATH = "all_features.npz"
MODEL_PATH = "data/models/svm_baseline.pkl"
METRICS_PATH = "data/models/svm_metrics.json"

# 加载数据
data = np.load(FEATURE_PATH, allow_pickle=True)
X = data["X"]
y = data["y"]

# 划分训练/测试集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 标准化
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 训练 SVM
model = LinearSVC(max_iter=5000, class_weight="balanced")
model.fit(X_train, y_train)

# 预测与评估
y_pred = model.predict(X_test)

acc = accuracy_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred).tolist()
report = classification_report(y_test, y_pred, output_dict=True)

print("=== SVM Baseline (LinearSVC, 3-class) ===")
print("Accuracy:", acc)
print("Confusion Matrix:\n", cm)
print("Classification Report:\n", classification_report(y_test, y_pred))

# 保存模型
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(model, MODEL_PATH)

# 保存评估指标
metrics = {
    "accuracy": acc,
    "confusion_matrix": cm,
    "classification_report": report
}
with open(METRICS_PATH, "w") as f:
    json.dump(metrics, f, indent=2)
