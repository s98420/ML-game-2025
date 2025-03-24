import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# 讀取遊戲數據
with open("log\game_log.pickle", "rb") as f:
    data = pickle.load(f)

features = []
labels = []
prev_ball_x, prev_ball_y = None, None

for i, record in enumerate(data):
    features.append([record["ball_pos"][0], record["ball_pos"][1], record["platform_x"]
                     , record["ball_delta"][0], record["ball_delta"][1], record["dir"], record["near_brick"]])
    if record["command"] == "MOVE_LEFT":
        label = -1
    elif record["command"] == "MOVE_RIGHT":
        label = 1
    else:
        label = 0
    #print(label)
    labels.append(label)


# 分割訓練與測試數據
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.1, random_state=42)

# 訓練 KNN 模型
knn = KNeighborsClassifier(n_neighbors=2)
knn.fit(X_train, y_train)

# 評估模型準確度
y_pred = knn.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"模型準確度: {accuracy:.2f}")

# 儲存模型
with open("log/arkanoid_knn_model.pickle", "wb") as f:
    pickle.dump(knn, f)

print("模型已儲存！")
