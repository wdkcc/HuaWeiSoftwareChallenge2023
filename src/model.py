import math
from common import workbench_constraint, workbench_is_robot_target_buy, map_type_id, robot_target_buy, robot_target_sell
from typing import List
class Plot():
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
    def plot_distance(self, x, y):
        return math.sqrt(math.pow(self.x - x, 2) + math.pow(self.y - y, 2))

class Workbench():
    def __init__(self):
        self.type = None # 范围[1, 9]
        self.plot = None
        self.remaining_production_time = None # -1：表示没有生产. 0：表示生产因输出格满而阻塞. >=0：表示剩余生产帧数。
        self.material_grid_status = None # 二进制位表描述，例如 48(110000)表示拥有物品 4 和 5。
        self.product_grid_status = None # 产品格状态

    def get_distance_to_other_plot(self, plot: Plot):
        """输入一个点，返回该机器人到该点的距离"""
        return math.sqrt(math.pow(self.plot.x - plot.x, 2) + math.pow(self.plot.y - plot.y, 2))

    def get_bin_material_status(self):
        return '{:010b}'.format(self.material_grid_status)

    def is_full_material_grid(self):
        material_status = self.get_bin_material_status()
        for can_sell_item_type in workbench_constraint[self.type]:
            status_index = -can_sell_item_type - 1
            if material_status[status_index] != "1":
                return False
        return True
    def lack_material_type(self):
        """返回当前工作台缺乏的材料"""
        lack_type = []
        material_status = self.get_bin_material_status()
        for can_sell_item_type in workbench_constraint[self.type]:
            status_index = -can_sell_item_type - 1
            if material_status[status_index] == "0":
                lack_type.append(can_sell_item_type)
        return lack_type


class Robot():
    def __init__(self):
        self.workbench_id = None # 所处工作台 ID
        self.item_type = None # 携带物品类型
        self.time_factor = None # 时间价值系数
        self.crash_factor = None # 碰撞价值系数
        self.angle_speed = None # 角速度
        self.x_y_line_speed = None # 线速度
        self.direction = None # 朝向
        self.plot = Plot()
        self.id = -1
        self.distance_to_target = 100
        self.distance_sell = 0
        self.target_plot = None

    def get_distance_to_other_plot(self, plot: Plot):
        """输入一个点，返回该机器人到该点的距离"""
        return math.sqrt(math.pow(self.plot.x - plot.x, 2) + math.pow(self.plot.y - plot.y, 2))
    def get_angle_to_other_plot(self, plot: Plot):
        """输入一个点，返回该机器人到该点的角度[0, pi] [0, -pi]"""
        y_err = (plot.y - self.plot.y)+ 1e-19
        x_err = plot.x - self.plot.x
        if (y_err > 0) and (x_err < 0):
            return math.atan(y_err / (x_err + 1e-19)) + math.pi
        elif (y_err < 0) and (x_err < 0):
            return math.atan(y_err / (x_err + 1e-19)) - math.pi
        else:
            return math.atan(y_err / (x_err + 1e-19))

    def get_include_angle(self, workbench_plot: Plot):
        """根据当前机器人朝向，and计算机器人与工作台角度。得到机器人朝向与机器人到工作台的夹角[0, pi] [0, -pi]"""
        robot_direction = self.direction
        robot_workbench_angle = self.get_angle_to_other_plot(workbench_plot)
        # 转换范围至[0, 2*pi]
        if robot_direction < 0:
            robot_direction = 2 * math.pi + robot_direction
        # 转换范围至[0, 2*pi]
        if robot_workbench_angle < 0:
            robot_workbench_angle = 2 * math.pi + robot_workbench_angle
        angle_speed = robot_workbench_angle - robot_direction
        # 取夹角最小的那边
        if angle_speed < -math.pi:
            angle_speed = angle_speed + 2 * math.pi
        if angle_speed > math.pi:
            angle_speed = angle_speed - 2 * math.pi
        return angle_speed

    def get_angle_speed(self, workbench_plot: Plot):
        """根据当前机器人朝向，and计算机器人与工作台角度。得到机器人转动角速度"""
        angle_speed = self.get_include_angle(workbench_plot)
        return angle_speed*16

    def get_line_speed(self, workbench_plot: Plot):
        """计算机器人到工作台的距离和机器人朝向与到工作台角度的夹角，得到线速度"""
        distance = self.get_distance_to_other_plot(workbench_plot)
        angle = self.get_include_angle(workbench_plot)
        if map_type_id["type"] == 3:
            if abs(angle) >= math.pi * 3 / 10:
                return -0.5
            else:
                return 6

        if map_type_id["type"] == 1:
            if abs(angle) >= math.pi / 4 and distance <= 1:
                return 1
            elif abs(angle) >= math.pi / 2 and distance <= 3.5:
                return -1
            elif abs(angle) >= math.pi * 3 / 5:
                return 4
            elif abs(angle) >= math.pi * 2 / 5:
                return -1
            else:
                return 6

        if map_type_id["type"] == 4:
            if abs(angle) >= math.pi / 4 and distance <= 1:
                return 1
            elif abs(angle) >= math.pi / 2 and distance <= 3:
                return -1
            elif abs(angle) >= math.pi * 3 / 5:
                return 4
            elif abs(angle) >= math.pi * 2 / 5:
                return -0.5
            else:
                return 6

        if abs(angle) >= math.pi / 4 and distance <= 1:
            return 1
        elif abs(angle) >= math.pi / 2 and distance <= 3:
            return -1
        elif abs(angle) >= math.pi * 3 / 5:
            return 4
        elif abs(angle) >= math.pi * 2 / 5:
            return -1
        else:
            return 6


    def get_angle_line_speed(self, workbench_plot: Plot):
        # 计算机器人转动角速度
        angle_speed = self.get_angle_speed(workbench_plot)
        # 计算机器人与工作台之间距离
        distance = self.get_distance_to_other_plot(workbench_plot)
        # 记录到目标点及到目标点的距离
        self.target_plot = workbench_plot
        self.distance_to_target = distance
        # 计算线速度
        line_speed = self.get_line_speed(workbench_plot)
        return angle_speed, line_speed

    def get_cur_line_speed(self):
        return math.sqrt(math.pow(self.x_y_line_speed[0], 2) + math.pow(self.x_y_line_speed[1], 2))

    def get_time_to_plot(self, plot: Plot):
        distance = self.get_distance_to_other_plot(plot)
        angle = abs(self.get_include_angle(plot))
        t_a = angle/math.pi
        t_d = distance/6
        return t_d+t_a
    def search_workbench(self, workbench_plot: Plot, lack_material_type: List, workbenchs: List[Workbench]):
        middle_plot = Plot(x=(self.plot.x+workbench_plot.x)/2, y=(self.plot.y+workbench_plot.y)/2)
        r = self.get_distance_to_other_plot(workbench_plot)/2
        for wbi, wb in enumerate(workbenchs):
            for mt in lack_material_type:
                if wb.type == mt and wb.get_distance_to_other_plot(middle_plot) <= r and workbench_is_robot_target_buy[wbi] == False:
                    return wbi
        return None

    def get_target_wbi(self):
        if robot_target_buy[self.id] != -1:
            return robot_target_buy[self.id]
        elif robot_target_sell[self.id] != -1:
            return robot_target_sell[self.id]
        else:
            return None

class Operate():
    def __init__(self, angle_speed, line_speed, buy_flag, sell_flag):
        self.angle_speed = angle_speed
        self.line_speed = line_speed
        self.buy_flag = buy_flag
        self.sell_flag = sell_flag
