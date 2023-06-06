def robots_path_better(robots: List[Robot], workbenchs: List[Workbench]):
    def sort_fun_by_weight(arr):
        return arr[-2]

    robots_buy_sell_path = []
    robots_id_list = []
    for rid in range(4):
        if robot_target_buy[rid] == -1 and robot_target_sell[rid] == -1:
            robots_id_list.append(rid)
    while len(robots_id_list) > 0:
        tem_robots_operate = []
        for rid in robots_id_list:
            distance_robot_to_buy_sell_workbenchs = get_robot_and_workbenchs_buy_sell_distance(robots[rid], workbenchs)
            distance_robot_to_buy_sell_workbenchs[0].append(rid)
            tem_robots_operate.append(copy.deepcopy(distance_robot_to_buy_sell_workbenchs[0]))
        tem_robots_operate.sort(key=sort_fun_by_weight)
        robots_buy_sell_path.append(copy.deepcopy(tem_robots_operate[0]))
        bwi = tem_robots_operate[0][0]
        swi = tem_robots_operate[0][2]
        rid = tem_robots_operate[0][-1]

        workbench_is_robot_target_buy[bwi] = True
        robot_target_buy[rid] = bwi
        workbench_is_robot_target_sell[swi * 100 + workbenchs[bwi].type] = True
        robot_target_sell[rid] = swi

        robots_id_list.remove(tem_robots_operate[0][-1])
    return robots_buy_sell_path