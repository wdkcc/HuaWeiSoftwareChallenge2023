workbench_constraint = {}
workbench_constraint[1] = []
workbench_constraint[2] = []
workbench_constraint[3] = []
workbench_constraint[4] = [1, 2]
workbench_constraint[5] = [1, 3]
workbench_constraint[6] = [2, 3]
workbench_constraint[7] = [4, 5, 6]
workbench_constraint[8] = [7]
workbench_constraint[9] = [i for i in range(1, 8)]

# item_price[1] = 3000
# item_price[2] = 3200
# item_price[3] = 3400
# item_price[4] = 7100
# item_price[5] = 7800
# item_price[6] = 8300
# item_price[7] = 29000
map_type_id = {} # 地图类型
workbench_type_nums = {} # 统计工作台数据

item_price = {}
item_price[1] = 3
item_price[2] = 10
item_price[3] = 12
item_price[4] = 9
item_price[5] = 7
item_price[6] = 12
item_price[7] = 12

workbench_is_robot_target_buy = {} # 是否已经被机器人锁定为目标
workbench_is_robot_target_sell = {} #
robot_target_buy = {} # 机器人买的目标：-1代表机器人无目标
robot_target_sell = {} # 机器人卖的目标：-1代表机器人无目标





# distance_robot_to_workbenchs = []