import random
import pickle
import os
import math

"""
The template of the main script of the machine learning process
"""


class MLPlay:
    def __init__(self,ai_name, *args, **kwargs):
        """
        Constructor
        """
        self.snapshot = {
            "frame": -1,
            "status": "GAME_OVER",
            "ball": (0, 0),
            "ball_served": False,
            "platform": (0, 400),
            "bricks": [],
            "hard_bricks": []
        }
        # 切球預留的位置
        #self.acc_space = 15
        # 平台對目標位置容許的誤差量
        self.PLATFORM_TOLERANCE = 5
        self.last_command = "NONE"
        self.game_history = []
        if not os.path.exists("log"):
            os.makedirs("log")
        print(ai_name)

    def is_even(self, num):
        if int(num / 2) == int((num - 1) / 2):
            return False
        else:
            return True
        
    def platform_control(self, scene_info, predict_x, default= "NONE"):
        command = default
        if (predict_x - scene_info["platform"][0]) > (20 + self.PLATFORM_TOLERANCE):
            command = "MOVE_RIGHT" 
        elif  (predict_x - scene_info["platform"][0]) < (20 - self.PLATFORM_TOLERANCE):
            command = "MOVE_LEFT" 
        return command
    
   
    def update(self, scene_info, *args, **kwargs):
        """
        Generate the command according to the received `scene_info`.
        """
        # 1 = 右上
        # 2 = 左上
        # 3 = 左下
        # 4 = 右下
        near_brick = 0
        close_brick_x = 0
        close_brick_y = 0
        close_dis = 200
        ball_dx = 0
        ball_dy = 0
        dir = 0
        hit = False

        if (scene_info["status"] == "GAME_OVER" or scene_info["status"] == "GAME_PASS"):
            return "RESET"
        

        # 發球
        if not scene_info["ball_served"]:
            command = "SERVE_TO_LEFT"
            return command

        else:



            # 預設為100
            predict_x = 100
            # 第一幀
            if self.snapshot["frame"] == -1:
                command = "NONE"
            else:
                ball_dx = (scene_info["ball"][0] - self.snapshot["ball"][0]) / (scene_info["frame"] - self.snapshot["frame"])
                ball_dy = (scene_info["ball"][1] - self.snapshot["ball"][1]) / (scene_info["frame"] - self.snapshot["frame"])
                
                if ball_dx >= 0 and ball_dy >=0:
                    dir = 4
                elif ball_dx >= 0 and ball_dy < 0:
                    dir = 1
                elif ball_dx < 0 and ball_dy >= 0:
                    dir = 3
                elif ball_dx < 0 and ball_dy < 0:
                    dir = 2

                # 球往上就跟著跑
                if ball_dy <= 0 and scene_info["ball"][1] > 200:
                    predict_x = scene_info["ball"][0]
                    if predict_x > 120:
                        predict_x = 120
                    if predict_x < 80:
                        predict_x = 80
                    
                elif  ball_dy <= 0 and scene_info["ball"][1] < 150:
                    predict_x = 100
                elif  ball_dy <= 0: 
                    predict_x = scene_info["platform"][0]
                
                # 球往下在下半就預測，上半就到中間
                elif ball_dy > 0:
                    ball_arrive_plat_frame = abs(scene_info["platform"][1] - scene_info["ball"][1]) / abs(ball_dy)
                    predict_x = scene_info["ball"][0] + ball_arrive_plat_frame * ball_dx

                    while predict_x > 200 or predict_x < 0:
                        if predict_x > 200:
                            if self.is_even(int(predict_x / 200)):
                                predict_x = abs(predict_x - int(predict_x / 200) * 200)
                            else:
                                predict_x = 200 - abs(predict_x - int(predict_x / 200) * 200)
                        elif predict_x < 0:
                            if self.is_even(int(predict_x / 200)):
                                predict_x = 200 + abs(predict_x + int(predict_x / 200) * 200)
                            else:
                                predict_x = abs(predict_x + int(predict_x / 200) * 200)
                
                for brick_x, brick_y in scene_info["bricks"] + scene_info["hard_bricks"]:
                    for i in range(10):
                        if scene_info["ball"][0] + (ball_dx * i) >= brick_x and scene_info["ball"][0] + (ball_dx * i) <= brick_x + 25:
                            if scene_info["ball"][1] + (ball_dy * i) >= brick_y and scene_info["ball"][1] + (ball_dy * i) <= brick_y + 10:
                                close_brick_x = brick_x
                                close_brick_y = brick_y
                                hit = True
                                close_dis = math.dist(scene_info["ball"], (brick_x + 12.5, brick_y + 5))
                                if brick_x - scene_info["ball"][0] >= 0:
                                    if brick_y - scene_info["ball"][1] >= 0:
                                        near_brick = 4
                                    else:
                                        near_brick = 1
                                else:
                                    if brick_y - scene_info["ball"][1] >= 0:
                                        near_brick = 3
                                    else:
                                        near_brick = 2

                if ball_dy < 0 and hit:
                    predict_x = close_brick_x + ((ball_dx / abs(ball_dx)) * 63)
                elif ball_dy > 0 and hit:
                    predict_x = close_brick_x - ((ball_dx / abs(ball_dx)) * 63)

                if hit:
                    while predict_x > 200 or predict_x < 0:
                        if predict_x > 200:
                            if self.is_even(int(predict_x / 200)):
                                predict_x = abs(predict_x - int(predict_x / 200) * 200)
                            else:
                                predict_x = 200 - abs(predict_x - int(predict_x / 200) * 200)
                        elif predict_x < 0:
                            if self.is_even(int(predict_x / 200)):
                                predict_x = 200 + abs(predict_x + int(predict_x / 200) * 200)
                            else:
                                predict_x = abs(predict_x + int(predict_x / 200) * 200)

                
                command = self.platform_control(scene_info, predict_x) 

        self.snapshot = scene_info
        

        record = {
            "ball_pos" : (scene_info["ball"][0], scene_info["ball"][1]),
            "platform_x" : scene_info["platform"][0],
            "ball_delta" : (ball_dx, ball_dy),
            "dir" : dir,
            "near_brick" : near_brick,
            "command" : command
        }
        self.game_history.append(record)
        #print(str(scene_info["frame"]) + " " + command)
        #print(scene_info["frame"])"""
        #print(hit)
        #print("predict x :" + str(predict_x) + " platform x :" + str(scene_info["platform"][0]) + " ball x:" + str(scene_info["ball"][0]))
        self.snapshot = scene_info
        self.last_command = command
        return command

    def reset(self):
        """
        Reset the status
        """
        
        path = "log/game_log.pickle"
        if os.path.exists(path):
            with open(path, "rb") as f:
                try:
                    old_data = pickle.load(f)
                except EOFError:
                    old_data = []  # 檔案可能是空的
        else:
            old_data = []

        # 將新的 game_history 附加到舊數據
        old_data.extend(self.game_history)

        # 寫回 pickle 檔案
        with open(path, "wb") as f:
            pickle.dump(old_data, f)
        
        self.game_history = []
        self.ball_served = False