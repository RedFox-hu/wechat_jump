# -*- coding:utf-8 -*-
import subprocess
from PIL import Image
import time
import random
import os


def get_screen():
    """手机截屏并保存为 screenshot.png"""
    process = subprocess.Popen("adb shell screencap -p", shell=True, stdout=subprocess.PIPE)
    screenshot = process.stdout.read()

    # 保存截图,注意windows环境中需要替换'\r\r\n'
    # screenshot = screenshot.replace(b'\r\n', b'\n')    # windows 环境打开这句注释

    with open("screenshot.png", "wb") as f:
        f.write(screenshot)


def jump(distance):
    press_time = distance * 1.392  # 按压时间系数：720p->2.099, 1080p->1.392, 2K->1.045
    press_time = max(press_time, 200)  # 按压时间不小于200ms

    # 随机生成按压范围
    x1 = random.randint(815, 923)
    y1 = random.randint(1509, 1658)
    x2 = x1 + random.randint(1, 3)
    y2 = y1 + random.randint(1, 3)
    # 构造adb命令
    cmd = "adb shell input swipe {0} {1} {2} {3} {4}".format(x1, y1, x2, y2, int(press_time))
    print("[JUMP]", cmd)
    subprocess.Popen(cmd, shell=True)


def find_piece_board(img_path):
    img = Image.open(img_path)
    img_width, img_height = img.size
    img_pixel = img.load()
    # init k
    k = 0.584

    # 优化搜索范围
    # 以50为步长搜索,定位start_y
    start_y = 0
    for y in range(int(img_height / 4), int(img_height * 3 / 4), 50):
        first_pt = img_pixel[0, y]
        for x in range(1, img_width):
            pt = img_pixel[x, y]
            if (pt[0] != first_pt[0]) or (pt[1] != first_pt[1]) or (pt[2] != first_pt[2]):
                start_y = y - 50
                break
        if start_y:
            break

    range_x = (int(img_width / 8), int(img_width * 7 / 8))
    range_y = (start_y, int(img_height * 2 / 3))

    # 定位棋子位置
    x_list = []
    y_list = []
    for y in range(range_y[0], range_y[1]):
        for x in range(range_x[0], range_x[1]):
            pt = img_pixel[x, y]
            if (50 < pt[0] < 60) and (53 < pt[1] < 63) and (95 < pt[2] < 105):
                x_list.append(x)
                piece_x = (min(x_list) + max(x_list)) // 2
                y_list.append(y)
        x_list.clear()

    piece_y = max(y_list) - 17
    # print("[FIND] piece's center point:({0}, {1})".format(piece_x, piece_y))

    # 确定棋盘位置
    # 优化棋盘搜索区域
    if piece_x < img_width / 2:
        board_start_x = piece_x + 40
        board_end_x = img_width
    else:
        board_start_x = 0
        board_end_x = piece_x - 40

    # 查找board顶点
    board_x = []
    for y in range(range_y[0], range_y[1]):
        first_pt = img_pixel[0, y]
        for x in range(board_start_x, board_end_x):
            pt = img_pixel[x, y]
            if abs(pt[0] - first_pt[0]) + abs(pt[1] - first_pt[1]) + abs(pt[2] - first_pt[2]) > 10:
                board_x.append(x)
                board_top_x = (min(board_x) + max(board_x)) // 2
                board_top_y = y
                break
        if len(board_x):
            break
    board_top_pixel = img_pixel[board_top_x, board_top_y]

    # 棋盘中心点和定点X坐标一样
    board_bottom_x = board_top_x
    for y in range(board_top_y + 300, board_top_y, -1):
        pt = img_pixel[board_top_x, y]
        if abs(pt[0]-board_top_pixel[0]) + abs(pt[1]-board_top_pixel[1]) +abs(pt[2]-board_top_pixel[2]) < 10:
            board_bottom_y = y
            break

    board_center_x = board_top_x

    if board_bottom_y - board_top_y < 20:
        board_center_y = int(piece_y - abs(piece_x - board_top_x) * k)
    else:
        board_center_x = int((board_top_x + board_bottom_x) / 2)
        board_center_y = int((board_top_y + board_bottom_y) / 2)
    # print("[FIND] board's top point:({0}, {1})".format(board_top_x, board_top_y))
    # print("[FIND] board's center point:({0}, {1})".format(board_center_x, board_center_y))
    # print("[FIND] board's bottom point:({0}, {1})".format(board_bottom_x, board_bottom_y))

    return (piece_x, piece_y), (board_center_x, board_center_y)


def main():
    """Main Function"""
    oper = input("Make sure adb is connected. Ready to jump? y/n:")
    if oper != 'y':
        exit()

    while True:
        get_screen()
        piece, board = find_piece_board("screenshot.png")
        print("[FIND] piece's point:", piece)
        print("[FIND] board's point:", board)

        # culate distance
        distance = ((piece[0] - board[0]) ** 2 + (piece[1] - board[1]) ** 2) ** 0.5

        # jump
        jump(distance)
        time.sleep(random.randrange(3, 5))  # 随机暂停


if __name__ == "__main__":
    main()



