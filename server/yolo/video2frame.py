# -*- coding: utf-8 -*-


import cv2
import os

def video2frame(videos_path,frames_save_path,time_interval):

  '''
  :param videos_path: 视频的存放路径
  :param frames_save_path: 视频切分成帧之后图片的保存路径
  :param time_interval: 保存间隔
  :return:
      
  '''

  vidcap = cv2.VideoCapture(videos_path)
  success, image = vidcap.read()
  count = 0
  
  while success:
    success, image = vidcap.read()
    count += 1

    if count % time_interval == 0:
      cv2.imencode('.jpg', image)[1].tofile(frames_save_path + "/%.6d.jpg" % count)
    # if count == 20:
    #   break
  print(count)

 
if __name__ == '__main__':
   videos_path = '../test.mp4'
   frames_save_path = './frame/orig/'#need to be modified
   time_interval = 1#隔一帧保存一次,can be modified
   video2frame(videos_path, frames_save_path, time_interval)
   #os.system("ls -R ./frame/orig/*.jpg > ./frame/orig/input.txt") this command placed to the main function
