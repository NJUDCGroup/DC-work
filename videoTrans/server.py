#!coding=utf-8

import threading
import socket
import struct
import os
import numpy
import cv2 as cv
import time
class Server():
    def __init__(self):
        pass
    def setup(self,ip,port):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # 绑定端口为9001
            self.s.bind((ip, port))
            # 设置监听数
            self.s.listen(10)
        except socket.error as msg:
            print (msg)
            sys.exit(1)
        print("setup finish")
        
    def serverStart(self,server_method):
        print ('Waiting connection...')
        
        while 1:
            # 等待请求并接受(程序会停留在这一旦收到连接请求即开启接受数据的线程)
            conn, addr = self.s.accept()
            # 接收数据
            t = threading.Thread(target=server_method, args=(conn, addr))
            t.start()
     
     
def deal_data(conn, addr):
    print ('Accept new connection from {0}'.format(addr))
    # conn.settimeout(500)
    # 收到请求后的回复
    conn.send('Hi, Welcome to the server!'.encode('utf-8'))
 
    while 1:
        # 申请相同大小的空间存放发送过来的文件名与文件大小信息
        fileinfo_size = struct.calcsize('128sl')
        # 接收文件名与文件大小信息
        buf = conn.recv(fileinfo_size)
        # 判断是否接收到文件头信息
        if buf:
            # 获取文件名和文件大小
            filename, filesize = struct.unpack('128sl', buf)
            fn = filename.strip(b'\00')
            fn = fn.decode()
            print ('file new name is {0}, filesize if {1}'.format(str(fn),filesize))
 
            recvd_size = 0  # 定义已接收文件的大小
            # 存储在该脚本所在目录下面
            fp = open('./' + str(fn), 'wb')
            print ('start receiving...')
            
            # 将分批次传输的二进制流依次写入到文件
            while not recvd_size == filesize:
                if filesize - recvd_size > 1024:
                    data = conn.recv(1024)
                    recvd_size += len(data)
                else:
                    data = conn.recv(filesize - recvd_size)
                    recvd_size = filesize
                fp.write(data)
            fp.close()
            print ('end receive...')
            
            os.chdir('../server/yolo')
            os.system('./darknet detect cfg/yolov3-tiny.cfg yolov3-tiny.weights ../{0}'.format(str(fn)))
            
            pred = 'predictions.jpg'
            fileinfo_size = struct.calcsize('128sl')
            # 定义文件头信息，包含文件名和文件大小
            fhead = struct.pack('128sl', os.path.basename(pred).encode('utf-8'), os.stat(pred).st_size)
            # 发送文件名称与文件大小
            conn.send(fhead)
        
            # 将传输文件以二进制的形式分多次上传至服务器
            fp = open(pred, 'rb')
            while 1:
                data = fp.read(1024)
                if not data:
                    print ('{0} file send over...'.format(os.path.basename(pred)))
                    break
                conn.send(data)
            
        # 传输结束断开连接
        conn.close()
        break   
def deal_video_data(conn,addr):
    print ('Accept new connection from {0}'.format(addr))
    # conn.settimeout(500)
    # 收到请求后的回复
    print("start recving video")
    conn.send('Hi, Welcome to the server!'.encode('utf-8'))
    fps = conn.recv(16).decode().strip(' ')
    print("video fps is \'{}\'".format(fps))
    
    sleepTime = int(1000/float(fps))
    while 1:
        length = conn.recv(16) #首先接收来自客户端发送的大小信息        
        if isinstance(length,str):
            len = int(length)
            stringData = conn.recv(len)
            # 对接收到的内容解码为图片形式
            data = numpy.fromstring(stringData,dtype='uint8')
            decimg = cv.imdecode(data,1)
            # 播放画面
            cv.imshow('SERVER',decimg)
        else:
            break
        if cv.waitKey(sleepTime)==ord('q'):
            break
    print("video done!")
    conn.close()
    
           
        
     
if __name__ == "__main__":
    server = Server()
    server.setup('127.0.0.1',8002)
    server.serverStart(deal_video_data)  
            