# -*- coding: utf-8 -*-


import os

os.system("python video2frame.py")
os.system("./darknet detect cfg/yolov3-tiny.cfg yolov3-tiny.weights")
os.system("python frame2video.py")
