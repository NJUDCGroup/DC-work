# -*- coding: utf-8 -*-


import os
import time
from multiprocessing import Process
def detect(d,i):
    os.system("./{} detect cfg/yolov3-tiny.cfg yolov3-tiny.weights".format(d))
    print("{} done!".format(d))

s = time.time()
#os.system("python video2frame.py")
#os.system("ls -R ./frame/orig/*.jpg > ./frame/orig/input.txt")

os.system("ls -R ./frame/orig1/*.jpg > ./frame/orig1/input.txt")
os.system("ls -R ./frame/orig2/*.jpg > ./frame/orig2/input.txt")
ps = []
for d in ["darknet1","darknet2"]:
    p = Process(target=detect,args=(d,1))
    ps.append(p)
    p.start()
#os.system("./darknet detect cfg/yolov3-tiny.cfg yolov3-tiny.weights")
while True:
    e = ps.__len__()
    for th in ps:
        if not th.is_alive():
            e -= 1
    if e <= 0:
        break

print("task done")
print(time.time()-s)
#os.system("python frame2video.py")
