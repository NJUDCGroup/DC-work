#!coding=utf-8

import threading
import socket
import struct
import os
import numpy
import cv2 as cv
import time
import re
from multiprocessing import Process,Value 
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
class Server():
    def __init__(self):
        pass
    def setup(self,ip,port):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # 绑定端口
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
     
     
 
def deal_video_data(conn,addr):
    running = Value('i',1)
    yolo_running = Value('i',1)
    task_kill = Value('i',0)
    process_num = 3
    process_recv = Process(target=recv_video,args=(conn,addr,process_num,running,task_kill))
    
    process_recv.start()
    #recv_video(conn,addr,process_num,running,task_kill)
    
    
    yolo_processes = []
    
    for i in range(process_num):
        p = Process(target=yolo_video,args=(i,running,task_kill))
        yolo_processes.append(p)
        p.start()
    ''''''
    
    sleepTime = 41
    process_play = Process(target=playVideo,args=(conn,addr,sleepTime,yolo_running,'./yolo/frame/pred/',task_kill))
    process_play.start()
    
    startTime = time.time() 
    while True:
        e = yolo_processes.__len__()
        for th in yolo_processes:
            if not th.is_alive():
                e -= 1
        if e <= 0:
            yolo_running.value = 0
            print("yolo running stop!")
            endTime = time.time()
            print("yolo time:{}".format(endTime-startTime))
            break
        '''
        if cv.waitKey(1) == ord('q'):
            task_kill.value = 1
            break
        '''
        time.sleep(1)
    # cv.destroyAllWindows()
    
    conn.close()

def recv_video(conn,addr,pronum,running,task_kill):
    print ('Accept new connection from {0}'.format(addr))
    # conn.settimeout(500)
    # 收到请求后的回复
    print("start recving video")
    conn.send('Hi, Welcome to the server!'.encode('utf-8'))
    fps = conn.recv(16).decode().strip(' ')
    print("video fps is \'{}\'".format(fps))
    
    sleepTime = int(1000/float(fps))
    startTime = time.time()
    count = 0
    frames_save_pathes = ["./yolo/frame/orig{}".format(i) for i in range(pronum)]
    print(task_kill.value)
    while task_kill.value == 0:
        length = conn.recv(16) #首先接收来自客户端发送的大小信息        
        if isinstance(length,str) and length:
            print(length)
            l = int(length)
            if l < 0:
                print('quit')
                break
            
            count += 1
            stringData = conn.recv(l)
            # 对接收到的内容解码为图片形式
            data = numpy.fromstring(stringData,dtype='uint8')
            
            decimg = cv.imdecode(data,1)
            cv.imencode('.jpg', decimg)[1].tofile(frames_save_pathes[count%pronum] + "/%.6d.jpg" % count)
 
            # 播放画面
            #cv.imshow('SERVER',decimg)
        else:
            print("quit")
            break
        '''
        if cv.waitKey(sleepTime)==ord('q'):
            break
        '''
    running.value = 0
    print("recv time: ",time.time()-startTime)
    print("video recv done!")




def yolo_video(id,running,task_kill):
    os.chdir('./yolo')
    dir_path = "./frame/orig{}".format(id)
    count = 0
    while not task_kill.value:
        os.system("ls -R ./frame/orig{}/*.jpg > ./frame/orig{}/input.txt".format(id,id))
        im_dir = os.listdir(dir_path)
        if len(im_dir)<=1:
            if not running.value:
                
                break
            print("empty")
            time.sleep(0.5)
            continue
        count += len(im_dir) - 1
        os.system("./darknet{} detect cfg/yolov3-tiny.cfg yolov3-tiny.weights".format(id))
        os.system("cat ./frame/orig{}/input.txt |xargs rm -rf".format(id))
    print("process {} finish {} images".format(id,count))     
    return count    
    

 
def playVideo(conn,addr,sleepTime,yolo_running,im_dir,task_kill):
    q = []
    print("play start")
    conn.send("start".ljust(10).encode())
    picture_cache_size = 30
    while not task_kill.value:
        im_list = os.listdir(im_dir)
        if not yolo_running.value and not im_list:
            print("play process end!")
            break   
        im_list.sort()
        print(im_list)
        if not im_list:
            time.sleep(10)
            continue
        im_part = im_list[:picture_cache_size]
        im_tosend = [int(re.findall(r"\d+",i)[0]) for i in im_part]
        #print(im_tosend)
        if len(im_tosend)<picture_cache_size and yolo_running.value:
            print("wait for more to send {}".format(yolo_running.value))
            time.sleep(10)
            continue
        c = -1
        for i in range(len(im_tosend)-1):  # 连续性检验
            if im_tosend[i]+1 == im_tosend[i+1]:
                pass
            else:
                c = i
        if c>=0:
            print("wait for img {}".format(im_tosend[c]))
            time.sleep(5)
            continue
        
        for i in im_part:
            print("send {}".format(i))
            im_name = os.path.join(im_dir+i)
            img = cv.imread(im_name)
            if img is None or img.size==0:
                os.remove(im_name)
                continue
            result,imgencode = cv.imencode(".jpg",img)
            data = numpy.array(imgencode)
            stringData = data.tostring()
            # print(len(stringData))
            conn.send(str(len(stringData)).ljust(16).encode())
            conn.send(stringData)
            q.append(img)
            os.remove(im_name)
        
        
        
    conn.send(str(-1).ljust(16).encode())
    print("send back over")    
        
    '''
    for f in q:
        cv.imshow('server',f)
        if cv.waitKey(sleepTime)==ord('q'):
            break
    '''

           
        
     
if __name__ == "__main__":
    
    server = Server()
    server.setup('127.0.0.1',8005)
    server.serverStart(deal_video_data)  
       
