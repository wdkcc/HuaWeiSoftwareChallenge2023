#!/bin/bash
import copy
import sys
from typing import List
from controller import get_robot_and_workbenchs_buy_sell_distance, robot_hit_control, wall_hit_control
from model import Robot, Workbench, Plot, Operate
from time import sleep
from math_sumilate import one_robot
import logging
import math
from common import workbench_constraint, workbench_is_robot_target_buy, workbench_is_robot_target_sell, robot_target_sell, robot_target_buy, workbench_type_nums, map_type_id


# with open('./log/example.log', encoding='utf-8', mode='w') as f:
#     f.write("log test\n")
# logging.basicConfig(filename='./log/example.log', level=logging.DEBUG)

def read_util_ok():
    map = []
    for i in range(100):
        line = sys.stdin.readline()
        map.append(line)
    ok = input()
    type6 = 0
    type7 = 0
    type8 = 0
    type9 = 0
    for row in map:
        for ele in row:
            if ele == "6":
                type6 += 1
            elif ele == "7":
                type7 += 1
            elif ele == "8":
                type8 += 1
            elif ele == "9":
                type9 += 1
    workbench_type_nums[6] = type6
    workbench_type_nums[7] = type7
    workbench_type_nums[8] = type8
    workbench_type_nums[9] = type9

    if workbench_type_nums[7] == 8:
        map_type_id["type"] = 1
    elif workbench_type_nums[6] == 4:
        map_type_id["type"] = 2
    elif workbench_type_nums[6] == 12:
        map_type_id["type"] = 3
    elif workbench_type_nums[6] == 3:
        map_type_id["type"] = 4
def read_workbenchs():
    """读取一帧工作台数据"""
    workbenchs = []
    k = int(sys.stdin.readline())
    for i in range(k):
        if workbench_is_robot_target_buy.get(i) == None:
            workbench_is_robot_target_buy[i] = False
        line = sys.stdin.readline()
        line = line.split(" ")
        workbench = Workbench()
        workbench.type = int(line[0])
        workbench.plot = Plot(x=float(line[1]), y=float(line[2]))
        workbench.remaining_production_time = int(line[3])
        workbench.material_grid_status = int(line[4])
        workbench.product_grid_status = int(line[5])
        for sell_item in workbench_constraint[workbench.type]:
            if workbench_is_robot_target_sell.get(i*10 + sell_item) == None:
                workbench_is_robot_target_sell[i*10 + sell_item] = False
        workbenchs.append(workbench)
    return workbenchs

def read_robots():
    robots = []
    for i in range(4):
        if robot_target_buy.get(i) == None:
            robot_target_buy[i] = -1
        if robot_target_sell.get(i) == None:
            robot_target_sell[i] = -1
        line = sys.stdin.readline()
        line = line.split(" ")
        robot = Robot()
        robot.id = i
        robot.workbench_id = int(line[0])
        robot.item_type = int(line[1])
        robot.time_factor = float(line[2])
        robot.crash_factor = float(line[3])
        robot.angle_speed = float(line[4])
        robot.x_y_line_speed = float(line[5]), float(line[6])
        robot.direction = float(line[7])
        robot.plot = Plot(x=float(line[8]), y=float(line[9]))
        robots.append(robot)
    ok = input()
    return robots

def finish():
    sys.stdout.write('OK\n')
    sys.stdout.flush()

def robots_path_better(robots: List[Robot], workbenchs: List[Workbench], robots_id_list):
    """求每个机器人到每条路的价值，优先为价值最高的机器人分配路径"""
    def sort_fun_by_weight(arr):
        return arr[-2]
    robots_buy_sell_path = []
    while len(robots_id_list) > 0:
        tem_robots_operate = []
        for rid in robots_id_list:
            distance_robot_to_buy_sell_workbenchs = get_robot_and_workbenchs_buy_sell_distance(robots[rid], workbenchs, robots, frame_id)
            if len(distance_robot_to_buy_sell_workbenchs) > 1:
                distance_robot_to_buy_sell_workbenchs.append(rid)
                tem_robots_operate.append(copy.deepcopy(distance_robot_to_buy_sell_workbenchs))
            else:
                return None
        tem_robots_operate.sort(key=sort_fun_by_weight)
        robots_buy_sell_path.append(copy.deepcopy(tem_robots_operate[0]))
        bwi = tem_robots_operate[0][0]
        swi = tem_robots_operate[0][2]
        rid = tem_robots_operate[0][-1]
        workbench_is_robot_target_buy[bwi] = True
        robot_target_buy[rid] = bwi

        workbench_is_robot_target_sell[swi * 10 + workbenchs[bwi].type] = True
        robot_target_sell[rid] = swi
        robots_id_list.remove(rid)
    return robots_buy_sell_path

# def robots_path_better(robots: List[Robot], workbenchs: List[Workbench], robots_id_list):
#     """求每个机器人到每条路的价值，优先为价值最高的机器人分配路径"""
#     def sort_fun_by_weight(arr):
#         return arr[-2]
#     robots_buy_sell_path = []
#     while len(robots_id_list) > 0:
#         tem_robots_operate = []
#         for rid in robots_id_list:
#             distance_robot_to_buy_sell_workbenchs = one_robot(robots[rid], workbenchs, robots)
#             if len(distance_robot_to_buy_sell_workbenchs) > 0:
#                 tem_robots_operate.append(distance_robot_to_buy_sell_workbenchs)
#             else:
#                 return None
#         tem_robots_operate.sort(key=sort_fun_by_weight)
#         robots_buy_sell_path.append(copy.deepcopy(tem_robots_operate[0]))
#
#         bwi = tem_robots_operate[0][0]
#         swi = tem_robots_operate[0][2]
#         rid = tem_robots_operate[0][-1]
#         workbench_is_robot_target_buy[bwi] = True
#         robot_target_buy[rid] = bwi
#         workbench_is_robot_target_sell[swi * 10 + workbenchs[bwi].type] = True
#         robot_target_sell[rid] = swi
#         robots_id_list.remove(tem_robots_operate[0][-1])
#
#     return robots_buy_sell_path

def get_angle_line_speed(workbenchs: List[Workbench], robots: List[Robot], operates: List):
    robots_not_target = []
    robots_have_target = []
    # 得到机器人哪些有目标，哪些无目标
    for rid in range(4):
        if robot_target_buy[rid] == -1 and robot_target_sell[rid] == -1:
            robots_not_target.append(rid)
        else:
            robots_have_target.append(rid)
    # 无目标机器人规划目标
    robots_path = robots_path_better(robots, workbenchs, robots_not_target)
    if robots_path != None:
        for bwi, buy_distance, swi, sell_distance, _, rid in robots_path:
            angle_speed = robots[rid].get_angle_speed(workbenchs[bwi].plot)
            robots[rid].distance_to_target = buy_distance
            robots[rid].distance_sell = sell_distance
            robots[rid].target_plot = workbenchs[bwi].plot
            # 计算机器人线速度
            line_speed = robots[rid].get_line_speed(workbenchs[bwi].plot)
            operates[rid] = Operate(angle_speed, line_speed, False, False)
    for rid in robots_have_target:
        buy_flag = False
        sell_flag = False
        robot = robots[rid]
        if robot.item_type == 0:
            angle_speed, line_speed = robot.get_angle_line_speed(workbenchs[robot_target_buy[robot.id]].plot)
            if robot.workbench_id == robot_target_buy[robot.id] and workbenchs[robot.workbench_id].product_grid_status == 1:
                buy_flag = True
            operates[rid] = Operate(angle_speed, line_speed, buy_flag, sell_flag)
        else:
            # 计算角速度，线速度
            angle_speed, line_speed = robot.get_angle_line_speed(workbenchs[robot_target_sell[robot.id]].plot)
            if robot.workbench_id == robot_target_sell[robot.id]:
                sell_flag = True
            operates[rid] = Operate(angle_speed, line_speed, buy_flag, sell_flag)

def get_distance_robots_to_workbenchs(robots: List[Robot], workbenchs: List[Workbench]):
    distance_robot_to_workbench = []
    for rid in range(len(robots)):
        tem = []
        for wid in range(len(workbenchs)):
            tem.append(robots[rid].get_distance_to_other_plot(workbenchs[wid].plot))
        distance_robot_to_workbench.append(tem)
    return distance_robot_to_workbench

if __name__ == '__main__':
    read_util_ok()
    finish()
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        parts = line.split(' ')
        frame_id, money = int(parts[0]), int(parts[1])  # 接收帧率ID和金钱
        # logging.info(f"id: {frame_id}")
        workbenchs = read_workbenchs()
        robots = read_robots()
        sys.stdout.write('%d\n' % frame_id)
        operates = []
        # 1. 基本的路线规划控制
        # 初始化
        for robot_id in range(4):
            operates.append(Operate(2, 2, False, False))
        # 路线控制
        get_angle_line_speed(workbenchs, robots, operates)
        # 2. 防止机器人之间相互碰撞控制
        robot_hit_control(operates, robots)
        # 3. 防止撞墙的控制并提交执行结果
        for robot_id in range(4):
            angle_speed, line_speed, buy_flag, sell_flag = operates[robot_id].angle_speed, operates[robot_id].line_speed, operates[robot_id].buy_flag, operates[robot_id].sell_flag
            line_speed = wall_hit_control(robots[robot_id], line_speed)
            sys.stdout.write('forward %d %d\n' % (robot_id, line_speed))
            sys.stdout.write('rotate %d %f\n' % (robot_id, angle_speed))
            if sell_flag:
                sys.stdout.write('sell %d\n' % (robot_id))
                # 出售完了解锁
                workbench_is_robot_target_sell[robot_target_sell[robot_id]*10 + robots[robot_id].item_type] = False
                robot_target_sell[robot_id] = -1
            bwi, swi = robot_target_buy[robot_id], robot_target_sell[robot_id]

            time = robots[robot_id].get_time_to_plot(workbenchs[swi].plot)
            if buy_flag and time * 50 <= 9000 - frame_id:
            # if buy_flag and workbenchs[bwi].get_distance_to_other_plot(workbenchs[swi].plot) / 6 * 50 <= 9000 - frame_id-5:
                sys.stdout.write('buy %d\n' % (robot_id))
                # 购买完了解锁
                workbench_is_robot_target_buy[robot_target_buy[robot_id]] = False
                robot_target_buy[robot_id] = -1
        finish()
