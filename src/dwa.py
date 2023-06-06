import logging
from common import map_type_id
from model import Robot, Operate, Plot
from typing import List
import math
# with open('./log/example.log', encoding='utf-8', mode='w') as f:
#     f.write("log test\n")
# logging.basicConfig(filename='./log/example.log', level=logging.DEBUG)
def get_bias_angle(a_b_angle: float, a_direction: float):
    """得到a_b_angle和a_direction之间的夹角[0, pi]"""
    if a_b_angle >= a_direction:
        if a_b_angle > math.pi / 2 and a_direction < -math.pi / 2:
            bias_angle = math.pi - a_b_angle + a_direction + math.pi
        else:
            bias_angle = a_b_angle - a_direction
        return bias_angle
    else:
        if a_direction > math.pi / 2 and a_b_angle < -math.pi / 2:
            bias_angle = math.pi - a_direction + a_b_angle + math.pi
        else:
            bias_angle = a_direction - a_b_angle
        return bias_angle


def is_angle_than_direction(to_angle, direction):
    """按范围是[0, 2*pi]的尺度比大小"""
    return (to_angle >= direction and not(to_angle>math.pi/2 and direction<-math.pi/2)) or (to_angle<-math.pi/2 and direction>math.pi/2)

def set_angle_speed(operates: List[Operate], a_id, b_id, max_angle_speed, a_is_correct, b_is_correct):
    if a_is_correct:
        operates[a_id].angle_speed = max_angle_speed
    if b_is_correct:
        operates[b_id].angle_speed = max_angle_speed

def hit_sumilate(robot_a: Robot, robot_b: Robot):
    time = 50
    plot_a = Plot(robot_a.plot.x, robot_a.plot.y)
    plot_b = Plot(robot_b.plot.x, robot_b.plot.y)
    for _ in range(1, time+1):
        plot_a.x += robot_a.x_y_line_speed[0] * 0.02
        plot_a.y += robot_a.x_y_line_speed[1] * 0.02
        plot_b.x += robot_b.x_y_line_speed[0] * 0.02
        plot_b.y += robot_b.x_y_line_speed[1] * 0.02
        if plot_a.plot_distance(plot_b.x, plot_b.y) <= 0.9:
            return True
    return False

def hit_turn_control(robot_a: Robot, robot_b: Robot, operates: List[Operate]):
    """同向而行的碰撞转向控制"""
    # 机器人目标工作台相同,就让距离远的减速
    if robot_a.get_target_wbi() == robot_b.get_target_wbi():
        if robot_a.distance_to_target > robot_b.distance_to_target:
            operates[robot_a.id].line_speed = 1
        else:
            operates[robot_b.id].line_speed = 1
        return
    # 机器人a朝向在第一象限
    if robot_a.direction >=0 and robot_a.direction <= math.pi/2:
        operates[robot_a.id].angle_speed = -math.pi
    # 机器人a朝向第二象限
    elif robot_a.direction >=math.pi and robot_a.direction <= math.pi:
        operates[robot_a.id].angle_speed = -math.pi
    # 机器人a朝向第三象限
    elif robot_a.direction >=-math.pi and robot_a.direction <= -math.pi/2:
        operates[robot_a.id].angle_speed = -math.pi
    # 机器人a朝向第四象限
    elif robot_a.direction >=-math.pi/2 and robot_a.direction <= 0:
        operates[robot_a.id].angle_speed = -math.pi

def robot_hit_check(robot_a: Robot, robot_b: Robot, operates: List[Operate]):
    a_is_correct = True
    b_is_correct = True
    if map_type_id["type"] == 2:
        if abs(robot_a.angle_speed) >= math.pi*3/4 or abs(robot_b.angle_speed) >= math.pi*3/4:
            return
    else:
        if abs(robot_a.angle_speed) >= math.pi*3/4 or abs(robot_b.angle_speed) == math.pi*3/4:
            return
    # 得到机器人间的距离
    d = 1.5
    if map_type_id["type"] == 2:
        d = 1
    distance = robot_a.get_distance_to_other_plot(robot_b.plot)
    if distance - robot_a.distance_to_target > d:
        a_is_correct = False
    if distance - robot_b.distance_to_target > d:
        b_is_correct = False

    a_b_angle = robot_a.get_angle_to_other_plot(robot_b.plot) # 得到机器人a到b的角度
    b_a_angle = robot_b.get_angle_to_other_plot(robot_a.plot) # 得到机器人b到a的角度
    ab_a_bias_angle = get_bias_angle(a_b_angle, robot_a.direction) # 得到机器人a到b的角度相对于a朝向角度的夹角
    b_bias_angle = get_bias_angle(robot_a.direction, robot_b.direction) # 得到机器人a, b朝向的夹角
    if ab_a_bias_angle >= math.pi/2 or b_bias_angle <= math.pi/2: # 如果a不是对着b走或者b不是对着a走则不操作
        # a,b同向而行
        if map_type_id["type"] == 3 or map_type_id["type"] == 1:
            if distance <= 3:
                if hit_sumilate(robot_a, robot_b):
                    hit_turn_control(robot_a, robot_b, operates)
                    return
        return

    max_angle_speed = math.pi
    a_bias_angle = get_bias_angle(a_b_angle, robot_a.direction)
    a_bias_distance = distance * math.sin(a_bias_angle) / 2
    b_bias_angle = get_bias_angle(b_a_angle, robot_b.direction)
    b_bias_distance = distance * math.sin(b_bias_angle) / 2

    # 此时a，b相向而行。
    if map_type_id["type"] == 1:
        if distance >= 4:
            return
    else:
        if distance >= 5:
            return
    if is_angle_than_direction(a_b_angle, robot_a.direction):
        if is_angle_than_direction(b_a_angle, robot_b.direction) == False:
            if abs(a_bias_distance-b_bias_distance) <= 1:
                if a_bias_angle < b_bias_distance:
                    set_angle_speed(operates, robot_a.id, robot_b.id, max_angle_speed, a_is_correct, b_is_correct)
                else:
                    set_angle_speed(operates, robot_a.id, robot_b.id, -max_angle_speed, a_is_correct, b_is_correct)
            else:
                return
        else:
            if abs(a_bias_distance+b_bias_distance) <= 1.1:
                set_angle_speed(operates, robot_a.id, robot_b.id, -max_angle_speed, a_is_correct, b_is_correct)
            else:
                return

    else:
        if is_angle_than_direction(b_a_angle, robot_b.direction):
            if abs(a_bias_distance - b_bias_distance) <= 1:
                if a_bias_angle < b_bias_distance:
                    set_angle_speed(operates, robot_a.id, robot_b.id, -max_angle_speed, a_is_correct, b_is_correct)
                else:
                    set_angle_speed(operates, robot_a.id, robot_b.id, max_angle_speed, a_is_correct, b_is_correct)
            else:
                return
        else:
            if abs(a_bias_distance + b_bias_distance) <= 1.1:
                set_angle_speed(operates, robot_a.id, robot_b.id, max_angle_speed, a_is_correct, b_is_correct)
            else:
                return

