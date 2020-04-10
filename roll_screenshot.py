import math
import operator
import os
import sys
import time
from functools import reduce

from PIL import Image
from PyQt5.QtCore import QThread, QTimer
from PyQt5.QtWidgets import QApplication
from pynput import mouse
from pynput.mouse import Controller as MouseController


class Splicing_shots(object):
    def __init__(self):
        self.init_splicing_shots_thread = Commen_Thread(self.init_splicing_shots)
        self.init_splicing_shots_thread.start()
        self.clear_timer = QTimer()
        self.clear_timer.timeout.connect(self.setup)

    def init_splicing_shots(self):
        """后台初始化"""
        self.img = []
        self.img_list = []
        self.images_data_line_list = []
        self.img_width = 0
        self.img_height = 0
        self.compare_row = 50
        self.cut_width = 0
        self.rate = 0.85
        self.roll_speed = 5
        self.min_head = 0
        self.left_border = 0
        self.right_border = 0
        self.head_pos = {}
        self.maybe_errorlist = []
        self.in_rolling = False
        self.arrange = 0
        self.max_arrange = 999
        if not os.path.exists("j_temp"):
            os.mkdir("j_temp")

    def setup(self):
        """清理&初始化"""
        if self.clear_timer.isActive():
            self.clear_timer.stop()
            print('clear')
        self.img = []
        self.img_list = []
        self.images_data_line_list = []
        self.img_width = 0
        self.img_height = 0
        self.compare_row = 50
        self.cut_width = 0
        self.rate = 0.85
        self.roll_speed = 3
        self.min_head = 0
        self.left_border = 0
        self.right_border = 0
        self.head_pos = {}
        self.maybe_errorlist = []
        self.in_rolling = False
        self.arrange = 0
        self.max_arrange = 999
        self.clear_timer = QTimer()
        self.clear_timer.timeout.connect(self.setup)

    def find_left_side(self):
        """寻找相同的左边界"""
        images_data_list = []
        for img in self.img_list[:2]:
            rotate_img = img.rotate(270, expand=1)
            rotate_img_data = list(rotate_img.convert('L').getdata())
            an_imgdata = []
            for line in range(rotate_img.height - 1):
                an_imgdata.append(rotate_img_data[line * rotate_img.width:(line + 1) * rotate_img.width])
            images_data_list.append(an_imgdata)
        rotate_height = len(images_data_list[0])
        min_head = rotate_height
        for i in range(1):
            for j in range(1, rotate_height):
                img1 = images_data_list[i][:j]
                img2 = images_data_list[i + 1][:j]
                if img2 != img1:
                    if j == 1:
                        print('没有重复左边界！')
                        return
                    elif j < (min_head + 1):
                        min_head = j - 1
                    break
        self.left_border = min_head
        print('minleft', min_head)

    def find_right_size(self):
        """寻找相同的右边界"""
        images_data_list = []
        for img in self.img_list[:2]:
            rotate_img = img.rotate(90, expand=1)
            rotate_img_data = list(rotate_img.convert('L').getdata())
            an_imgdata = []
            for line in range(rotate_img.height - 1):
                an_imgdata.append(rotate_img_data[line * rotate_img.width:(line + 1) * rotate_img.width])
            images_data_list.append(an_imgdata)
        rotate_height = len(images_data_list[0])
        min_head = rotate_height
        for i in range(1):
            for j in range(1, rotate_height):
                img1 = images_data_list[i][:j]
                img2 = images_data_list[i + 1][:j]
                # print(img2)
                if img2 != img1:
                    if j == 1:
                        print('没有重复右边界！')
                        self.right_border = self.img_width
                        # print(self.majority_color(self.images_data_line_list[0]))
                        return
                    elif j < (min_head + 1):
                        min_head = j - 1
                    break
        self.right_border = self.img_width - min_head
        print('minright', min_head)

    def find_the_same_head_to_remove(self):
        """寻找相同的头部(上边界)"""
        # if self.images_data
        min_head = self.img_height
        for i in range(len(self.img_list) - 1):
            for j in range(1, self.img_height):
                img1 = self.images_data_line_list[i][:j]
                img2 = self.images_data_line_list[i + 1][:j]
                # print(img2)
                if img2 != img1:
                    if j == 1:
                        print('没有重复头！')
                        # print(self.majority_color(self.images_data_line_list[0]))
                        return
                    elif j < (min_head + 1):
                        min_head = j - 1
                    break
        self.min_head = min_head
        print('minhead', min_head)

    def majority_color(self, classList):
        '''返回颜色列表中最多的颜色'''
        count_dict = {}
        for label in classList:
            if label not in count_dict.keys():
                count_dict[label] = 0
            count_dict[label] += 1
        # print(max(zip(count_dict.values(), count_dict.keys())))
        return max(zip(count_dict.values(), count_dict.keys()))

    def isthesameline(self, line1, line2):
        """判断是否两行是否相同"""
        same = 0
        rate = self.rate
        line1_majority_color = self.majority_color(line1)
        line2_majority_color = self.majority_color(line2)

        if line2_majority_color[1] != line1_majority_color[1]:
            # print(self.majority_color(line2),self.majority_color(line1))
            return 0
        elif abs(line1_majority_color[0] - line2_majority_color[0]) > self.img_width * (1 - rate) * 0.5:
            return 0
        else:
            majority_color_count, majority_color = line2_majority_color
            # print(majority_color_count,majority_color)
        if majority_color_count > int(self.cut_width * rate):
            return 1

        for i in range(self.cut_width):
            if line1[i] == majority_color or line2[i] == majority_color:
                # print('maj')
                continue
            else:
                if abs(line1[i] - line2[i]) < 10:
                    same += 1
        if same >= (self.cut_width - majority_color_count) * rate:
            return 1
        else:
            return 0

    def efind_the_pos(self):
        """在滚动的同时后台寻找拼接点"""
        while self.in_rolling or self.arrange < self.max_arrange:  # 如果正在截屏或截屏没有处理完
            print(self.arrange, '  max:', self.max_arrange)
            min_head = self.min_head
            left = self.left_border
            right = self.right_border
            self.cut_width = right - left
            images_data_line_list = self.images_data_line_list
            compare_row = self.compare_row
            i = self.arrange
            try:
                img1 = images_data_line_list[i]  # 前一张图片
                img2 = images_data_line_list[i + 1]  # 后一张图片
            except IndexError:
                time.sleep(0.1)  # 图片索引超出则等待下一张截屏
                continue
            max_line = [0, 0]
            for k in range(min_head, self.img_height - compare_row):  # 前一张图片从相同头部开始遍历到最后倒数compare_row行
                if self.in_rolling:  # 如果正在截屏则sleep一下避免过多占用主线程,也没什么用...
                    time.sleep(0.001)
                sameline = 0
                chance_count = 0
                chance = 0
                for j in range(min_head, min_head + compare_row):  # 后一张图片从相同头部开始逐行遍历compare_row行
                    lin1 = img1[k + sameline][left:right]
                    lin2 = img2[min_head + sameline][left:right]
                    if self.isthesameline(lin1, lin2):  # 如果是行相同,则sameline+1
                        sameline += 1
                        chance_count += 1
                        if chance_count >= 7:  # 每7行增加一个chance,避免误判
                            chance_count = 0
                            chance += 1
                        if sameline > max_line[1]:
                            max_line[0] = k
                            max_line[1] = sameline  # 记录最大行数备用
                    else:  # 否则chance-1直到退出
                        if chance <= 0:
                            break
                        else:
                            chance -= 1
                            sameline += 1

                if sameline >= compare_row - compare_row // 20:
                    self.head_pos[i] = k
                    print(i, k)
                    print(self.head_pos)
                    break
            if i not in self.head_pos.keys():#如果没有找到符合的拼接点,则取最大的配合点,并标记为可能出错的地方
                if max_line[1] >= 1:
                    self.head_pos[i] = max_line[0]
                    print(self.head_pos)
                    max_line.append(i)
                    self.maybe_errorlist.append(max_line)
                    print('max_line', i, max_line)  # 测试
            self.arrange += 1

    def find_the_pos(self):#和上面的efind_the_pos类似
        """寻找拼接点,当图片数少时可以直接截完屏调用"""
        min_head = self.min_head
        left = self.left_border
        right = self.right_border
        self.cut_width = right - left
        images_data_line_list = self.images_data_line_list
        compare_row = self.compare_row
        # print(min_head, self.img_height - compare_row)
        for i in range(len(self.img_list) - 1):
            # print(i)
            img1 = images_data_line_list[i]
            img2 = images_data_line_list[i + 1]
            max_line = [0, 0]  # 测试
            for k in range(min_head, self.img_height - compare_row):
                sameline = 0
                chance_count = 0
                chance = 0
                for j in range(min_head, min_head + compare_row):
                    lin1 = img1[k + sameline][left:right]
                    lin2 = img2[min_head + sameline][left:right]
                    # print(len(lin2),len(lin1))
                    res = self.isthesameline(lin1, lin2)
                    if res:
                        sameline += 1
                        chance_count += 1
                        if chance_count >= 5:
                            chance_count = 0
                            chance += 1
                        if sameline > max_line[1]:
                            max_line[0] = k
                            max_line[1] = sameline  # 测试
                        # print(i, j, k)
                    else:
                        # print(chance)
                        if chance <= 0:
                            break
                        else:
                            chance -= 1
                            sameline += 1

                if sameline >= compare_row - compare_row // 20:
                    self.head_pos[i] = k
                    print(i, k)
                    print(self.head_pos)
                    break
            if i not in self.head_pos.keys():
                if max_line[1] >= 1:
                    self.head_pos[i] = max_line[0]
                    print(self.head_pos)
                    max_line.append(i)
                    self.maybe_errorlist.append(max_line)
                    print('max_line', i, max_line)  # 测试

    def merge_all(self):
        """根据拼接点拼接所有图片"""
        majority_pos = self.majority_color(self.head_pos.values())
        for i in range(len(self.img_list) - 1):
            if i not in self.head_pos.keys():
                self.head_pos[i] = majority_pos[1]
                print(i, '丢失,补', majority_pos)  # 丢失则补为图片拼接点的众数,虽然没有什么用...
        img_width = self.img_width
        img_height = 0
        # head_pos = []
        # for i in len(self.head_pos)
        for i in self.head_pos.keys():
            img_height += self.head_pos[i] - self.min_head
            # print(img_height)
        img_height += self.img_height  # 加最后一张
        newpic = Image.new(self.img_list[0].mode, (img_width, img_height))
        height = 0
        if self.min_head:
            height += self.min_head
            newpic.paste(self.img_list[0].crop((0, 0, img_width, self.min_head)), (0, 0))
        for i in range(len(self.img_list) - 1):
            if self.min_head:
                newpic.paste(self.img_list[i].crop((0, self.min_head, self.img_width, self.head_pos[i])),
                             (0, height))
                height += self.head_pos[i] - self.min_head
            else:
                newpic.paste(self.img_list[i].crop((0, self.min_head, self.img_width, self.head_pos[i])),
                             (0, height))
                height += self.head_pos[i]
        if self.min_head:
            newpic.paste(self.img_list[-1].crop((0, self.min_head, img_width, img_height)), (0, height))
        else:
            newpic.paste(self.img_list[-1], (0, height))
        # name = str(time.strftime("%Y-%m-%d_%H.%M.%S", time.localtime()))
        newpic.save('j_temp/jam_outputfile.png')
        print('saved in j_temp/jam_outputfile.png')

    def is_same(self, img1, img2):
        """简单判断两幅图片是否相同,用于停止滚动截屏,速度非常快!"""
        h1 = img1.histogram()
        h2 = img2.histogram()
        result = math.sqrt(reduce(operator.add, list(map(lambda a, b: (a - b) ** 2, h1, h2))) / len(h1))
        if result <= 5:
            return True
        else:
            return False

    def auto_roll(self, area):
        """自动滚动截屏,总函数"""
        x, y, w, h = area
        self.img_width = w
        self.img_height = h
        speed = round(1 / self.roll_speed, 2)
        screen = QApplication.primaryScreen()
        controler = MouseController()
        find_left = Commen_Thread(self.find_left_side)
        find_right = Commen_Thread(self.find_right_size)
        find_head = Commen_Thread(self.find_the_same_head_to_remove)
        find_pos = Commen_Thread(self.efind_the_pos)
        threads = [find_left, find_pos, find_right, find_head]
        self.in_rolling = True
        i = 0
        img_height = 0
        controler.position = (area[0] + int(area[2] / 2), area[1] + int(area[3] / 2))
        while self.in_rolling:
            pix = screen.grabWindow(QApplication.desktop().winId(), x, y, w, h)  # 区域截屏获取图像pixmap
            img = Image.fromqpixmap(pix)  # 将qt的pixmap转为pil模块的img对象
            self.img_list.append(img)  # 储存图片的列表
            img_data = list(img.convert('L').getdata())  # 图片灰度化,并把灰度值转为列表
            an_img_line_data = []
            for line in range(h):
                an_img_line_data.append(img_data[line * w:(line + 1) * w])  # 列表分行储存
            self.images_data_line_list.append(an_img_line_data)
            if i >= 1:
                if self.is_same(self.img_list[i - 1], self.img_list[i]):  # 每帧检查是否停止(图片是否相同)
                    self.in_rolling = False
                    i += 1
                    break
                if img_height == 0:  # 图片有两张以上后,启动线程寻找图片边界点
                    img_height = 1
                    find_head.start()
                    find_left.start()
                    find_right.start()
                if i == 5:  # 图片大于5张才开始寻找拼接点
                    find_pos.start()
            controler.scroll(dx=0, dy=-3)  # 滚动屏幕
            time.sleep(speed)  # 速度控制
            # img.save('j_temp/{0}.png'.format(i))
            i += 1
        print('图片数', i)
        self.max_arrange = i - 1  # 获取图片序列用于控制寻找边界点的结束
        for thread in threads:  # 遍历并等待各线程结束
            thread.wait()
            # print(thread)
        if i <= 2:
            print('过短！一张图还不如直接截呐')
            self.clear_timer.start(0)
            return
        elif i <= 5:
            self.find_the_pos()  # 图片小于5张则截完屏在拼接
        else:
            find_pos.wait()  # 等待拼接点寻找完成
        # self.find_the_pos()
        print('found_pos_done')
        # try:
        self.merge_all()  # 调用图片拼接函数
        # except:
        #     print('拼接出错错误!请重新截屏！')
        #     self.clear_timer.start(10000)
        #     return
        print('可能错误的地方:', self.maybe_errorlist)
        self.clear_timer.start(10000)  # 10s后初始化内存


def listen():
    """鼠标监听,截屏中当按下鼠标停止截屏"""
    global listener
    print("listen")

    def on_click(x, y, button, pressed):
        if button == mouse.Button.left:
            if roller.in_rolling:
                roller.in_rolling = False

    listener = mouse.Listener(on_click=on_click)
    listener.start()


class Commen_Thread(QThread):
    """造的轮子...可用于多线程中不同参数的输入"""

    def __init__(self, action, *args):
        super(QThread, self).__init__()
        self.action = action
        self.args = args
        # print(self.args)

    def run(self):
        print('start_thread')
        if self.args:
            if len(self.args) == 1:
                self.action(self.args[0])
                print(self.args[0])
            elif len(self.args) == 2:
                self.action(self.args[0], self.args[1])
        else:
            self.action()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    roller = Splicing_shots()
    listen()
    roller.auto_roll((350, 50, 800, 700))
    sys.exit(app.exec_())
