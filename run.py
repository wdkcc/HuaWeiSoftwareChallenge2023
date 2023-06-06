import os
import json
root = "src"


def all():
    seed_num = 8
    all_score = 0
    for seed in range(seed_num):
        tem_score = 0
        for i in range(1, 5):
            result = os.popen(f'Robot.exe -fm new_maps/{i}.txt -s {seed * 100} -c {root} "python main.py"')
            score = json.loads(result.read())["score"]
            tem_score += score
        all_score += tem_score
        print(f"{seed * 100}: {tem_score}")
    print(all_score / seed_num)

def alone():
    all_score = 0
    for i in range(1, 5):
        result = os.popen(f'Robot.exe -fm new_maps/{i}.txt -s 300 -c {root} "python main.py"')
        score = json.loads(result.read())["score"]
        all_score += score
        print(f"{i} : {score}")
    print(all_score)

def all_one_map():
    seed_num = 8
    all_score = 0
    for seed in range(seed_num):
        tem_score = 0
        result = os.popen(f'Robot.exe -fm new_maps/3.txt -s {seed * 100} -c {root} "python main.py"')
        score = json.loads(result.read())["score"]
        tem_score += score
        all_score += tem_score
        print(f"{seed * 100}: {tem_score}")
    print(all_score / seed_num)

def run():
    tem_score = 0
    result = os.popen(f'Robot_gui.exe -m new_maps/3.txt -s 100 -c {root} "python main.py"')
    score = json.loads(result.read())["score"]
    tem_score += score
    print(tem_score)
if __name__ == '__main__':
    run()
