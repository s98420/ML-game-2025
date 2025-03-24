import random
import pickle
import os
import math

"""
The template of the main script of the machine learning process
"""
with open("log/arkanoid_knn_model.pickle", "rb") as f:
    knn = pickle.load(f)

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
        
        print(ai_name)
        
    
    def update(self, scene_info, *args, **kwargs):
        """
        Generate the command according to the received `scene_info`.
        """
        near_brick = 0
        close_brick_x = 0
        close_brick_y = 0
        close_dis = 200
        ball_dx = 0
        ball_dy = 0
        dir = 0
        hit = False
        # 1.運動方向跟前一幀相同嗎 是->2 否->3
        # 2.有預測過了嗎 有->保持 無->3
        # 3.球往上嗎 是->4 否->檢查碰撞並預測反彈後路徑
        # 4.球在下半畫面嗎 是->檢查碰撞並預測反彈後路徑 否-> 回到中央
        
        # 重開遊戲
        if (scene_info["status"] == "GAME_OVER" or
                scene_info["status"] == "GAME_PASS"):
            return "RESET"
        
        # 發球
        if not scene_info["ball_served"]:
            command = "SERVE_TO_LEFT"
            #"SERVE_TO_LEFT"

            return command
        else:
            ball_x, ball_y = scene_info["ball"]
            platform_x = scene_info["platform"][0]
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

        action = knn.predict([[ball_x, ball_y, platform_x, ball_dx, ball_dy, dir, near_brick]])[0]
        if action == -1:
            command = "MOVE_LEFT"
        elif action == 1:
            command = "MOVE_RIGHT"
        elif action == 0:
            command = "NONE"

        #print(command)
        self.snapshot = scene_info
        return command

    def reset(self):
        """
        Reset the status
        """
        self.ball_served = False