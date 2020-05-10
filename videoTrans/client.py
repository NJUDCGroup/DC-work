# -*- coding: UTF-8 -*-

import socket
import threading
import struct
import sys,os
import cv2 as cv
import numpy
class Client():
    def __init__(self):
        pass
        
    def setup(self,serverip,port):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((serverip,port))
        except socket.error as msg:
            print(msg)
            sys.exit(1)
        print(self.s.recv(1024))
    def sendIMG(self,filepath):        
        if not os.path.isfile(filepath):
            print("wrong filepath")
            sys,exit(1)
        else:
            # 定义定义文件信息。128s表示文件名为128bytes长，l表示一个int或log文件类型，在此为文件大小
            fileinfo_size = struct.calcsize('128sl')
            # 定义文件头信息，包含文件名和文件大小
            fhead = struct.pack('128sl', os.path.basename(filepath).encode('utf-8'), os.stat(filepath).st_size)
            # 发送文件名称与文件大小
            self.s.send(fhead)
            
            # 将传输文件以二进制的形式分多次上传至服务器
            fp = open(filepath, 'rb')
            while 1:
                data = fp.read(1024)
                if not data:
                    print ('{0} file send over...'.format(os.path.basename(filepath)))
                    break
                self.s.send(data)
            return fileinfo_size
    def recvIMG(self,fileinfo_size):
        buf = self.s.recv(fileinfo_size)
        if buf:
            # 获取文件名和文件大小
            filename, filesize = struct.unpack('128sl', buf)
            fn = filename.strip(b'\00')
            fn = fn.decode()
            print ('Predictions received!')
 
            recvd_size = 0  # 定义已接收文件的大小
            # 存储在该脚本所在目录下面
            fp = open('./' + str(fn), 'wb')
            # 将分批次传输的二进制流依次写入到文件
            while not recvd_size == filesize:
                if filesize - recvd_size > 1024:
                    data = self.s.recv(1024)
                    recvd_size += len(data)
                else:
                    data = self.s.recv(filesize - recvd_size)
                    recvd_size = filesize
                fp.write(data)
            fp.close()
            print("successfully save!")
    def closeSocket(self):
        self.s.close()
        
        
    def sendVideo(self,filepath):
        if not os.path.isfile(filepath):
            print("wrong filepath")
            sys.exit(1)
        else:
            cap = cv.VideoCapture(filepath)
            encode_param=[int(cv.IMWRITE_JPEG_QUALITY),90] #设置编码参数
            if cap.isOpened(): #获取视频帧率
                fps = cap.get(cv.CAP_PROP_FPS)
                sleepTime = int(1000/fps)
                # 发送视频帧率
                self.s.send(str(fps).ljust(8))
                
            print("start send video , fps:{}".format(fps))
            
            while cap.isOpened():
                ret, frame = cap.read() # 每次读出视频的一帧
                if not ret:
                    print("can't receive frame (strea, end?). Exiting...")
                    break
                
                #cv.imshow('本地视频播放',frame)
                #if cv.waitKey(sleepTime)==ord('q'): # q键结束播放
                #    break
                
                # 对当前帧做压缩编码
                result, imgencode = cv.imencode('.jpg',frame)
                data = numpy.array(imgencode)
                stringData = data.tostring()
                # 首先发送图片编码后的长度
                self.s.send(str(len(stringData)).ljust(16).encode())
                # 然后发送图片内容
                self.s.send(stringData)
                if cv.waitKey(sleepTime) == ord('q'):
                    print("video sending has been break")
                    break
            print("video sending over!")
            cap.release()
                
if __name__ == '__main__':
    client = Client()
    client.setup('127.0.0.1',8002)

    #size = client.sendIMG('dog.jpg')
    #client.recvIMG(size)
    client.sendVideo('/mnt/f/video/test3.mp4')
    client.closeSocket()