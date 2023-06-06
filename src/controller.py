import logging
import math
from model import Workbench, Robot, Operate
from typing import List
from common import workbench_constraint, workbench_is_robot_target_buy, workbench_is_robot_target_sell, robot_target_sell, robot_target_buy, item_price, map_type_id
from dwa import robot_hit_check

def get_wall_limit_speed(s_max, angle):
    r = 0.53
    s = math.pi*r*r
    m = s*20
    F = 250
    a = F / m
    rotate_F = 50
    rotate_a = rotate_F/m
    v0 = 6
    s = 0
    v1 = 1
    while(s < s_max):
        v1 += 0.1
        t0 = (v0-v1)/a
        t1 = v1/rotate_a
        s0 = v0*t0-a*t0*t0/2
        s1 = v1*t1-rotate_a*t1*t1/2
        s = s0+s1
    return (v1-0.2)/math.cos(angle)


def who_sell_target_is_this_workbench(bwi):
    for rid in range(4):
        if robot_target_sell[rid] == bwi:
            return rid
    return None

def buy_wb_is_other_robot_sell_target(bwi, workbench_type):
    for can_sell_item_type in workbench_constraint[workbench_type]:
        if workbench_is_robot_target_sell[bwi*10 + can_sell_item_type] == True:
            return True
    return False

def who_buy_target_is_this_workbench(bwi):
    for rid in range(4):
        if robot_target_buy[rid] == bwi:
            return rid
    return None

def get_robot_and_workbenchs_buy_sell_distance(robot: Robot, workbenchs: List[Workbench], robots: List[Robot], frame_id=None)->List:
    """输入工作台列表和机器人，返回按权重排序后最佳的机器人到买-卖工作台之间的路径(工作台序号, 距离)"""
    distance_robot_workbenchs = []
    for index, workbench in enumerate(workbenchs):
        distance = robot.get_distance_to_other_plot(workbench.plot)
        if map_type_id["type"] == 3:
            time = robot.get_time_to_plot(workbench.plot)
            distance = time*6.0
        if map_type_id["type"] == 1:
            inter_val = 7
            condition = (workbench.product_grid_status == 1 or (workbench.remaining_production_time >= 0 and distance/6*1000 > (workbench.remaining_production_time*20+25))) and (workbench_is_robot_target_buy[index] == False or workbenchs[index].type<=3 and abs(robots[who_buy_target_is_this_workbench(index)].get_distance_to_other_plot(workbenchs[index].plot)-robot.get_distance_to_other_plot(workbenchs[index].plot)) >= inter_val)
        else:
            condition = (workbench.product_grid_status == 1 or (workbench.remaining_production_time >= 0 and distance / 6 * 1000 > (workbench.remaining_production_time * 20 + 25))) and workbench_is_robot_target_buy[index] == False
        if condition:
            distance_robot_workbenchs.append([index, distance])
    distance_buyWorkbench_sellWorkbench = get_best_path_buy_sell_workbench(workbenchs, distance_robot_workbenchs, robots, frame_id)
    return distance_buyWorkbench_sellWorkbench

def lack_material_workbench_type7(workbenchs: List[Workbench], type=7):
    """返回类型7缺乏的材料和最紧缺的材料类型"""
    lack_materials = []
    for wi, workbench in enumerate(workbenchs):
        if workbench.type == type:
            lack_materials.extend(workbench.lack_material_type())
    best_lack_material_type = None
    material_type4 = 0
    material_type5 = 0
    material_type6 = 0
    for lm in lack_materials:
        if lm == 4:
            material_type4+=1
        elif lm == 5:
            material_type5 += 1
        elif lm == 6:
            material_type6 += 1
    if material_type4 > material_type5 and material_type4 > material_type6:
        best_lack_material_type = 4
    elif material_type5 >= material_type4 and material_type5 >= material_type6:
        best_lack_material_type = 5
    elif material_type6 >= material_type4 and material_type6 >= material_type4:
        best_lack_material_type = 6
    return lack_materials, best_lack_material_type

def map1_lack_material_workbench_type7(workbenchs: List[Workbench], type=7):
    """返回类型7缺乏的材料和最紧缺的材料类型"""
    lack_materials = []
    type4_generation = 0
    type5_generation = 0
    type6_generation = 0
    for wi, workbench in enumerate(workbenchs):
        if workbench.type == type:
            lack_materials.extend(workbench.lack_material_type())
        if workbench.type == 4:
            if workbench.remaining_production_time >0:
                type4_generation += 1
            if workbench.product_grid_status == 1:
                type4_generation += 1
        elif workbench.type == 5:
            if workbench.remaining_production_time >0:
                type5_generation += 1
            if workbench.product_grid_status == 1:
                type5_generation += 1
        elif workbench.type == 6:
            if workbench.remaining_production_time >0:
                type6_generation += 1
            if workbench.product_grid_status == 1:
                type6_generation += 1

    lack_item_nums = [[4, 0], [5, 0], [6, 0]]
    for lm in lack_materials:
        if lm == 4:
            lack_item_nums[0][1] += 1
        elif lm == 5:
            lack_item_nums[1][1] += 1
        elif lm == 6:
            lack_item_nums[2][1] += 1
    def sort_by_num(arr):
        return arr[1]
    lack_item_nums[0][1] -= type4_generation
    lack_item_nums[1][1] -= type5_generation
    lack_item_nums[2][1] -= type6_generation
    lack_item_nums.sort(key=sort_by_num)
    best_lack_material_type = lack_item_nums[-1][0]
    if lack_item_nums[0][1] == lack_item_nums[1][1] == lack_item_nums[2][1]:
        return lack_materials, None
    return lack_materials, best_lack_material_type

def is_lack_material_workbench_type7(type: int, type7_lack_materials: List):
    for lack_material_type in type7_lack_materials:
        if lack_material_type == type:
            return True
    return False

def is_robot_target(wi, w_type):
    for item_type in workbench_constraint[w_type]:
        if workbench_is_robot_target_sell[wi*10 + item_type] == True:
            return True
    return False

def get_best_path_buy_sell_workbench(workbenchs: List[Workbench], distance_robot_and_workbenchs: List, robots: List[Robot], frame_id=None):
    """得到买的工作台到卖的工作台距离"""
    best_path = [1000000]
    for bwi, buy_distance in distance_robot_and_workbenchs:
        # 如果工作台已经生产好商品或者将要生产好商品，但已经有机器人去该工作台卖东西了，就不安排机器人去购买了。
        if buy_wb_is_other_robot_sell_target(bwi, workbenchs[bwi].type):
            rid = who_sell_target_is_this_workbench(bwi)
            # if robots[rid].get_distance_to_other_plot(workbenchs[bwi].plot) <= buy_distance or workbenchs[bwi].product_grid_status == 1:
            if robots[rid].get_distance_to_other_plot(workbenchs[bwi].plot) <= buy_distance:
                continue
        for swi, _ in enumerate(workbenchs):
            for can_sell_item_type in workbench_constraint[workbenchs[swi].type]:
                material_status = '{:010b}'.format(workbenchs[swi].material_grid_status)
                status_index = -can_sell_item_type - 1
                sell_distance = workbenchs[bwi].get_distance_to_other_plot(workbenchs[swi].plot)
                if map_type_id["type"] == 3:
                    is_no_lock = workbench_is_robot_target_sell[swi * 10 + can_sell_item_type] == False or workbenchs[swi].type == 9
                else:
                    is_no_lock = workbench_is_robot_target_sell[swi * 10 + can_sell_item_type] == False
                if can_sell_item_type == workbenchs[bwi].type and (material_status[status_index] == "0" or (workbenchs[swi].is_full_material_grid() and workbenchs[swi].product_grid_status == 0 and (buy_distance+sell_distance)/6*50 > (workbenchs[swi].remaining_production_time+2.8))) and is_no_lock:
                # if can_sell_item_type == workbenchs[bwi].type and material_status[status_index] == "0" and workbench_is_robot_target_sell[swi*10+can_sell_item_type] == False:
                    weight = sell_distance+buy_distance - workbenchs[bwi].type*3 if workbenchs[bwi].type > 3 else sell_distance+buy_distance
                    type7_lack_materials, best_lack_material_type_w7 = lack_material_workbench_type7(workbenchs)
                    # 图1执行的操作
                    if map_type_id["type"] == 1:
                        type7_lack_materials, best_lack_material_type_w7 = map1_lack_material_workbench_type7(workbenchs)
                        bias = 5
                        if is_lack_material_workbench_type7(workbenchs[swi].type, type7_lack_materials):
                            weight -= 2
                        if best_lack_material_type_w7 != None:
                            if workbenchs[swi].type == best_lack_material_type_w7:
                                weight -= bias + 10
                        # 如果出售的目标是7，且7只差一个，就给他更小的损失权重

                        if workbenchs[swi].type == 7:
                            lack_material_num = len(workbenchs[swi].lack_material_type())
                            if lack_material_num == 2:
                                weight -= 2 + bias
                            if lack_material_num == 1:
                                weight -= 8 + bias
                        elif workbenchs[swi].type == 9 and workbenchs[bwi].type < 7:
                            weight += 5
                        elif workbenchs[swi].type >= 4 and workbenchs[swi].type <= 6:
                            lack_material_num = len(workbenchs[swi].lack_material_type())
                            if lack_material_num == 1:
                                weight -= 18
                        if workbenchs[swi].type >= 4 and workbenchs[swi].type <= 7:
                            if is_robot_target(swi, workbenchs[swi].type):
                                weight -= 10
                    # 图2执行的操作
                    elif map_type_id["type"] == 2:
                        bias = 12
                        if is_lack_material_workbench_type7(workbenchs[swi].type, type7_lack_materials):
                            weight -= 2
                        if workbenchs[swi].type == best_lack_material_type_w7:
                            weight -= bias
                        # 如果出售的目标是7，且7只差一个，就给他更小的损失权重
                        if workbenchs[swi].type == 7:
                            lack_material_num = len(workbenchs[swi].lack_material_type())
                            if lack_material_num == 2:
                                weight -= 2 + bias
                            if lack_material_num == 1:
                                weight -= 6 + bias
                        elif workbenchs[swi].type == 9 and workbenchs[bwi].type < 7:
                            weight += 5
                        elif workbenchs[swi].type >= 4 and workbenchs[swi].type <= 6:
                            lack_material_num = len(workbenchs[swi].lack_material_type())
                            if lack_material_num == 1:
                                weight -= 6
                    # 图四执行的操作
                    elif map_type_id["type"] == 4:
                        bias = 10
                        # if is_lack_material_workbench_type7(workbenchs[swi].type, type7_lack_materials):
                        #     weight -= 10
                        if workbenchs[bwi].type == 7:
                            weight -= 20
                        if workbenchs[swi].type == best_lack_material_type_w7:
                            weight -= bias
                        if workbenchs[swi].type == 4 and frame_id < 8250:
                                weight -= 30
                        elif workbenchs[swi].type == 4 and frame_id > 8250:
                                weight -= 1
                        # 如果出售的目标是7，且7只差一个，就给他更小的损失权重
                        if workbenchs[swi].type == 7:
                            lack_material_num = len(workbenchs[swi].lack_material_type())
                            if lack_material_num == 2:
                                weight -= 2 + bias
                            if lack_material_num == 2 and workbenchs[bwi] == 4:
                                weight -= 10
                            if lack_material_num == 1:
                                weight -= 15 + bias
                        elif workbenchs[swi].type >= 4 and workbenchs[swi].type <= 6:
                            lack_material_num = len(workbenchs[swi].lack_material_type())
                            if lack_material_num == 1:
                                weight -= bias
                    elif map_type_id["type"] == 3:
                        if workbenchs[swi].type == 9 and workbenchs[bwi].type < 7:
                            weight += 5
                        elif workbenchs[swi].type >= 4 and workbenchs[swi].type <= 6:
                            lack_material_num = len(workbenchs[swi].lack_material_type())
                            if lack_material_num == 1:
                                weight -= 6
                        if workbenchs[bwi].type == 6:
                            weight -= 0.5
                    if weight < best_path[-1]:
                        best_path = [bwi, buy_distance, swi, sell_distance, weight]
    return best_path

def get_distance_base_line_speed(line_speed):
    t = (line_speed-1)/14.164733276245581
    return (line_speed+1)*t/2

def wall_hit_control(robot: Robot, org_line_speed):
    bias_angle = math.pi/8
    # distance_limit = 1.85
    distance_bias = 0.9
    line_limit = 0.7
    # 机器人与左边界近且朝向左方
    if robot.direction >= (math.pi / 2 + bias_angle) or robot.direction <= -(math.pi / 2 + bias_angle):
        if robot.direction >= (math.pi / 2 + bias_angle):
            include_angle = math.pi - robot.direction
        else:
            include_angle = math.pi + robot.direction
        line_speed_x = math.cos(include_angle)*robot.get_cur_line_speed()
        distance_limit = get_distance_base_line_speed(line_speed_x)
        if robot.plot.x <= distance_limit+distance_bias:
            return line_limit
    # 机器人与右边界近且朝向右方
    if robot.direction <= (math.pi/2-bias_angle) and robot.direction >= -(math.pi/2-bias_angle):
        include_angle = abs(robot.direction)
        line_speed_x = math.cos(include_angle) * robot.get_cur_line_speed()
        distance_limit = get_distance_base_line_speed(line_speed_x)
        if robot.plot.x >= 50-distance_limit-distance_bias:
            return line_limit
    # 机器人与下边界近且朝向下方
    if robot.direction <= -bias_angle and robot.direction >= -(math.pi-bias_angle):
        include_angle = abs(-math.pi/2 - robot.direction)
        line_speed_x = math.cos(include_angle) * robot.get_cur_line_speed()
        distance_limit = get_distance_base_line_speed(line_speed_x)
        if robot.plot.y <= distance_limit+distance_bias:
            return line_limit

    # 机器人与上边界过近且朝向上方
    if robot.direction >= bias_angle and robot.direction <= (math.pi-bias_angle):
        include_angle = abs(math.pi / 2 - robot.direction)
        line_speed_x = math.cos(include_angle) * robot.get_cur_line_speed()
        distance_limit = get_distance_base_line_speed(line_speed_x)
        if robot.plot.y >= 50-distance_limit-distance_bias:
            return line_limit
    return org_line_speed

# def wall_hit_control(robot: Robot, org_line_speed):
#     bias_angle = math.pi/8
#     distance_limit = 1.85
#     flag = 1.8
#     # 机器人与左边界近且朝向左下方
#     if robot.plot.x <= distance_limit-flag and (robot.direction >= (math.pi/2+bias_angle) or robot.direction <= -(math.pi/2+bias_angle)) and robot.plot.y <= distance_limit-flag and robot.direction <= -bias_angle and robot.direction >= -(math.pi-bias_angle):
#         return 1
#     # 机器人与右下
#     if robot.plot.x >= 50-distance_limit+flag and robot.direction <= (math.pi/2-bias_angle) and robot.direction >= -(math.pi/2-bias_angle) and robot.plot.y <= distance_limit-flag and robot.direction <= -bias_angle and robot.direction >= -(math.pi-bias_angle):
#         return 1
#     # 机器人右边界
#     if robot.plot.x >= 50 - distance_limit and robot.direction <= (math.pi / 2 - bias_angle):
#         return 1
#     # 靠近左
#     if robot.plot.x <= distance_limit - flag and (robot.direction >= (math.pi / 2 + bias_angle)):
#         return 1
#     # 靠近下
#     if robot.plot.y <= distance_limit and robot.direction <= -bias_angle and robot.direction >= -(math.pi-bias_angle):
#         org_line_speed = 1
#     # 机器人与上边界过近且朝向上方
#     if robot.plot.y >= 50-distance_limit and robot.direction >= bias_angle and robot.direction <= (math.pi-bias_angle):
#         org_line_speed = 1
#     return org_line_speed

def robot_hit_control(operates: List[Operate], robots: List[Robot]):
    for robot_a_id in range(4):
        robot_b_id = robot_a_id + 1
        robot_a = robots[robot_a_id]
        while (robot_b_id < 4):
            robot_b = robots[robot_b_id]
            robot_hit_check(robot_a, robot_b, operates)
            robot_b_id += 1
