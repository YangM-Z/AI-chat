'''
文件名：dataVisualization.py
描述：负责数据可视化,MplCanvas的实例可作为widget被添加到pyqt布局中
      draw_chart(data)方法负责绘制图形
      draw()方法负责将绘制好的图形显示在widget上
'''

import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas




class MplCanvas(FigureCanvas):
    # 花瓣的文字，右上角开始，逆时针方向
    petalTexts = []

    # 花瓣的数值，右上角开始，逆时针方向
    petalValues = []

    # 花瓣颜色，右上角开始，逆时针方向
    petalColors = ['#E9B9C9', '#DB96A8', '#CD7488', '#BE5168', '#AE2E47']

    # 图片的背景颜色
    bkcolor = '#F1E5E5'

    # 字体
    fontFamily = 'SimHei'   # 黑体

    # 字体大小
    fontsize = 15

    # 花瓣的线宽
    petalLineWidth = 5.0

    # 花瓣离圆心的距离
    petalDistance = 3.2

    # 最大花瓣的半径
    maxRadius = 40.0

    # 两个圆的半径比例，数值越大，花瓣越尖
    petalLengthRatio = 3.5

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        fig.patch.set_facecolor(self.bkcolor)
        super(MplCanvas, self).__init__(fig)

    def draw_petal(self, angle, color, text, value, petalAngle):

        maxValue = max(self.petalValues)

        # 计算后续需要用到的角度
        angle1 = petalAngle/2
        angle2 = 90-angle1

        # 计算大圆半径
        R = self.maxRadius*(value/maxValue*0.5+0.5)
        # 计算小圆半径
        r = R/self.petalLengthRatio
        # 计算花瓣的实际旋转角度
        realAngle = angle + 90
        # 计算花瓣的相对原点
        Ox = 0.0
        Oy = -self.petalDistance
        # 计算旋转前小圆的圆心
        O1x = Ox
        O1y = Oy-r/np.sin(np.radians(angle1))
        # 计算旋转前大圆的圆心
        O2x = Ox
        O2y = Oy-R/np.sin(np.radians(angle1))
        # 计算旋转前ABCD点的坐标
        Ax = Ox-r*np.sin(np.radians(angle2))
        Ay = Oy-r*np.sin(np.radians(angle2))/np.tan(np.radians(angle1))
        Bx = O1x+r*np.sin(np.radians(angle2))
        By = Ay
        Cx = Ox+R*np.sin(np.radians(angle2))
        Cy = Oy-R*np.sin(np.radians(angle2))/np.tan(np.radians(angle1))
        Dx = Ox-R*np.sin(np.radians(angle2))
        Dy = Cy

        # 旋转全部点
        rotationO1x = O1x*np.cos(np.radians(realAngle))-O1y*np.sin(np.radians(realAngle))
        rotationO1y = O1x*np.sin(np.radians(realAngle))+O1y*np.cos(np.radians(realAngle))
        rotationO2x = O2x*np.cos(np.radians(realAngle))-O2y*np.sin(np.radians(realAngle))
        rotationO2y = O2x*np.sin(np.radians(realAngle))+O2y*np.cos(np.radians(realAngle))
        rotationAx = Ax*np.cos(np.radians(realAngle))-Ay*np.sin(np.radians(realAngle))
        rotationAy = Ax*np.sin(np.radians(realAngle))+Ay*np.cos(np.radians(realAngle))
        rotationBx = Bx*np.cos(np.radians(realAngle))-By*np.sin(np.radians(realAngle))
        rotationBy = Bx*np.sin(np.radians(realAngle))+By*np.cos(np.radians(realAngle))
        rotationCx = Cx*np.cos(np.radians(realAngle))-Cy*np.sin(np.radians(realAngle))
        rotationCy = Cx*np.sin(np.radians(realAngle))+Cy*np.cos(np.radians(realAngle))
        rotationDx = Dx*np.cos(np.radians(realAngle))-Dy*np.sin(np.radians(realAngle))
        rotationDy = Dx*np.sin(np.radians(realAngle))+Dy*np.cos(np.radians(realAngle))


        # 表示坐标
        O1=(rotationO1x,rotationO1y)
        O2=(rotationO2x,rotationO2y)
        A=(rotationAx,rotationAy)
        B=(rotationBx,rotationBy)
        C=(rotationCx,rotationCy)
        D=(rotationDx,rotationDy)

        # 绘制带线小圆
        smallcircleWithLine = plt.Circle(O1,r, color='white', ec='white', linewidth=self.petalLineWidth)
        self.ax.add_patch(smallcircleWithLine)
        # 绘制带线大圆
        bigcircleWithLine = plt.Circle(O2,R, color='white', ec='white', linewidth=self.petalLineWidth)
        self.ax.add_patch(bigcircleWithLine)
        # 绘制带线梯形
        trapezoidWithLine = plt.Polygon([A,B,C,D],closed=True, color='white', ec='white', linewidth=self.petalLineWidth)
        self.ax.add_patch(trapezoidWithLine)
        # 绘制不带线小圆
        smallcircleWithoutLine = plt.Circle(O1,r, color=color, ec='none')
        self.ax.add_patch(smallcircleWithoutLine)
        # 绘制不带线大圆
        bigcircleWithoutLine = plt.Circle(O2,R, color=color, ec='none')
        self.ax.add_patch(bigcircleWithoutLine)
        # 绘制不带线梯形
        trapezoidWithoutLine = plt.Polygon([A,B,C,D],closed=True, color=color, ec='none')
        self.ax.add_patch(trapezoidWithoutLine)

        # 添加文字
        matplotlib.rcParams['font.family'] = self.fontFamily  # 设置字体
        self.ax.text(rotationO2x, rotationO2y, text, ha='center', va='center', fontsize=self.fontsize, color='white')
        # 添加数值
        self.ax.text(rotationO2x, rotationO2y-self.fontsize, value, ha='center', va='center', fontsize=self.fontsize, color='white')
    
    def draw_chart(self,data):
        # 清空数据
        self.petalTexts = []
        self.petalValues = []
        for item in data:
            if item['total_messages'] == 0:
                continue
            self.petalTexts.append(item['username'])
            self.petalValues.append(item['total_messages'])

        petalNum = len(self.petalValues)
        if petalNum == 0:
            self.ax.axis('off')  # 关闭坐标轴显示
            return
        petalAngle = 360.0 / petalNum

        for i in range(petalNum):
            self.draw_petal(i * petalAngle + 90 - petalAngle / 2, self.petalColors[i], self.petalTexts[i], self.petalValues[i], petalAngle)

        self.ax.set_xlim(-self.maxRadius * 3, self.maxRadius * 3)
        self.ax.set_ylim(-self.maxRadius * 3, self.maxRadius * 3)
        self.ax.set_aspect('equal', 'box')  # 保持长度单位一致
        self.ax.axis('off')  # 关闭坐标轴显示
