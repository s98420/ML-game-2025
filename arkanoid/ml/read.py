import pickle

# 指定要讀取的 pickle 檔案
pickle_file = "log/game_log.pickle"

try:
    # 打開並讀取 pickle 檔案
    with open(pickle_file, "rb") as f:
        data = pickle.load(f)
    
    left = 0
    right = 0
    none = 0
    collision = 0
    # 印出 pickle 檔案的內容
    print("🔹 Pickle 檔案內容：")
    for i, record in enumerate(data):
        if record['command'] == "MOVE_LEFT":
            left = left + 1
        elif record['command'] == "MOVE_RIGHT":
            right = right + 1
        elif record['command'] == "NONE":
            none = none + 1
        #if record["collision"] == 1:
        #    collision = collision + 1
    print("left:" + str(left))
    print("right:" + str(right))
    print("none:" + str(none))
    #print("collision:" + str(collision))

except FileNotFoundError:
    print(f"❌ 檔案 '{pickle_file}' 不存在！請先運行遊戲並存儲記錄。")
except Exception as e:
    print(f"❌ 讀取 pickle 檔案時發生錯誤：{e}")
