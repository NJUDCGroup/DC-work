# -*- coding: utf-8 -*-


import os

os.system("python video2frame.py")
os.system("ls -R ./frame/orig/*.jpg > ./frame/orig/input.txt")
os.system("./darknet detect cfg/yolov3-tiny.cfg yolov3-tiny.weights")
os.system("python frame2video.py")
