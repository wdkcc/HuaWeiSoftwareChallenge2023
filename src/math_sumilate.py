import math
from model import Workbench, Robot
from typing import List
import copy
import logging
from common import workbench_constraint, workbench_is_robot_target_sell, workbench_is_robot_target_buy,robot_target_buy, robot_target_sell

# with open('./log/example.log', encoding='utf-8', mode='w') as f:
#     f.write("log test\n")
# logging.basicConfig(filename='./log/example.log', level=logging.DEBUG)
m = 17.649467527867458
item_price = {}
# item_price[1] = 3000
# item_price[2] = 3200
# item_price[3] = 3400
# item_price[4] = 7100
# item_price[5] = 7800
# item_price[6] = 8300
# item_price[7] = 29000

item_price[1] = 8
item_price[2] = 8.5
item_price[3] = 9
item_price[4] = 12
item_price[5] = 13
item_price[6] = 14
item_price[7] = 25


class Path():
    def __init__(self):
        self.bwi = None
        self.buy_distance = None
        self.swi = None
        self.sell_distance = None

def factor_function(x, maxX, minRate):
    part1 = 1 - math.sqrt(1-(1-x/maxX)**2)
    return part1*(1-minRate) + minRate

def get_profit_margin(spent_time, item_type):
    time_worth_factor = factor_function(spent_time*50, 9000, 0.8)
    # hit_worth_factor = factor_function(spent_time*10, 1000, 0.8)
    hit_worth_factor = 1
    return item_price[item_type] * time_worth_factor * hit_worth_factor


def who_sell_target_is_this_workbench(bwi):
    for rid in range(4):
        if robot_target_sell[rid] == bwi:
            return rid
    return None

def buy_wb_is_other_robot_sell_target(bwi, workbench_type):
    for can_sell_item_type in workbench_constraint[workbench_type]:
        if workbench_is_robot_target_sell[bwi*10 + can_sell_item_type] == True:
            # rid = who_sell_target_is_this_workbench(bwi)
            # distance = robots[rid].get_distance_to_other_plot(workbenchs[bwi].plot)
            # if workbenchs[bwi].remaining_production_time >=0 and distance/6*50 > workbenchs[bwi].remaining_production_time:
            return True
    return False

def get_robot_to_workbenchs_buy_distance(robot: Robot, workbenchs: List[Workbench], epoach):
    """输入工作台列表和机器人，返回排序后机器人和工作台之间的距离(工作台序号, 距离)"""
    distance_robot_workbenchs = []
    for bwi, workbench in enumerate(workbenchs):
        distance = robot.get_distance_to_other_plot(workbench.plot)
        if (workbench.product_grid_status == 1 or (workbench.remaining_production_time >= 0 and distance/6*50 > (workbench.remaining_production_time*+2-epoach*50))) and workbench_is_robot_target_buy[bwi] == False:
            distance_robot_workbenchs.append([bwi, distance])
    return distance_robot_workbenchs

def lack_material_workbench_type7(workbenchs: List[Workbench]):
    type7_lack_materials = []
    for wi, workbench in enumerate(workbenchs):
        if workbench.type == 7:
            type7_lack_materials.extend(workbench.lack_material_type())
    return type7_lack_materials

def is_lack_material_workbench_type7(type: int, type7_lack_materials: List):
    for lack_material_type in type7_lack_materials:
        if lack_material_type == type:
            return True
    return False

def get_sell_distance_workbench_to_worbenchs_distance(workbenchs: List[Workbench], distance_robot_and_workbenchs: List, robots: List[Robot], frame_id=None):
    distance_buyWorkbench_sellWorkbench = []
    for bwi, buy_distance in distance_robot_and_workbenchs:
        # 如果工作台已经生产好商品或者将要生产好商品，但已经有机器人去该工作台卖东西了，就不安排机器人去购买了。
        if buy_wb_is_other_robot_sell_target(bwi, workbenchs[bwi].type):
            rid = who_sell_target_is_this_workbench(bwi)
            if robots[rid].get_distance_to_other_plot(workbenchs[bwi].plot) <= buy_distance:
                continue
        for swi, _ in enumerate(workbenchs):
            for can_sell_item_type in workbench_constraint[workbenchs[swi].type]:
                material_status = '{:010b}'.format(workbenchs[swi].material_grid_status)
                status_index = -can_sell_item_type - 1
                sell_distance = workbenchs[bwi].get_distance_to_other_plot(workbenchs[swi].plot)
                if can_sell_item_type == workbenchs[bwi].type and (material_status[status_index] == "0" or (workbenchs[swi].is_full_material_grid() and workbenchs[swi].product_grid_status == 0 and (buy_distance+sell_distance)/6*50 > (workbenchs[swi].remaining_production_time+2.8))) and workbench_is_robot_target_sell[swi*10+can_sell_item_type] == False:
                # if can_sell_item_type == workbenchs[bwi].type and material_status[status_index] == "0" and workbench_is_robot_target_sell[swi*10+can_sell_item_type] == False:
                    weight = sell_distance + buy_distance - item_price[workbenchs[bwi].type]
                    distance_buyWorkbench_sellWorkbench.append([bwi, buy_distance, swi, sell_distance, weight])
    def sort_fun_by_type_weight(arr):
        return arr[-1]
    distance_buyWorkbench_sellWorkbench.sort(key=sort_fun_by_type_weight)
    if len(distance_buyWorkbench_sellWorkbench) >= 2:
        return distance_buyWorkbench_sellWorkbench[:2]
    else:
        return distance_buyWorkbench_sellWorkbench


def one_robot(robot: Robot, workbenchs: List[Workbench], robots: List[Robot]):
    temRoot = copy.deepcopy(robot)
    start = 0
    all_path = []
    # 回溯得到每条路径
    # logging.info(f"{robot.id}: start backtrace......")
    backtrace(temRoot, workbenchs, start, [], all_path, robots)
    # 整理每条路径权重
    all_path_weight = []
    weight = 0
    for distance_buy_workbenchs_to_sell_workbenchs in all_path:
        weight = distance_buy_workbenchs_to_sell_workbenchs[-1][-1]
        all_path_weight.append([weight, distance_buy_workbenchs_to_sell_workbenchs])
    def sort_fun_by_weight(arr):
        return arr[0]
    all_path_weight.sort(key=sort_fun_by_weight)
    # logging.info(f"{all_path_weight}")
    # logging.info(f"{all_path_weight[0]}")
    # logging.info(f"{all_path_weight[0][1]}")
    # logging.info("+++++++++++++++++")
    if len(all_path_weight) == 0:
        return []
    bwi, buy_distance, swi, sell_distance, _ = all_path_weight[0][1][0]

    # logging.info(f"++++++++++++++++++{[bwi, buy_distance, swi, sell_distance, weight, robot.id]}")
    return [bwi, buy_distance, swi, sell_distance, weight, robot.id]

# def mul_robots(robots: List[Robot], workbenchs: List[Workbench]):
#     robots_not_target = []
#     robots_have_target = []
#     for rid in range(4):
#         if robot_target_buy[rid] == -1 and robot_target_sell[rid] == -1:
#             robots_not_target.append(rid)
#         else:
#             robots_have_target.append(rid)
#     while(len(robots_not_target) > 0):
#         for rid in robots_not_target:


def backtrace(robot: Robot, workbenchs: List[Workbench], epoach, path: List, all_path: List, robots: List[Robot], all_weight=0):
    if epoach >= 2:
        all_path.append(copy.deepcopy(path))
        return
    distance_robot_workbenchs = get_robot_to_workbenchs_buy_distance(robot, workbenchs, epoach)
    distance_buy_workbenchs_to_sell_workbenchs = get_sell_distance_workbench_to_worbenchs_distance(workbenchs, distance_robot_workbenchs, robots)
    tem_len = len(path)
    for bwi, buy_distance, swi, all_distance, weight in distance_buy_workbenchs_to_sell_workbenchs:
        path.append([bwi, buy_distance, swi, all_distance, all_weight+weight])
        robot.plot = copy.deepcopy(workbenchs[swi].plot)
        backtrace(robot, workbenchs, epoach+1, path, all_path, robots, all_weight+weight)
        path = path[:tem_len]

if __name__ == '__main__':
    print(250/17.649467527867458)