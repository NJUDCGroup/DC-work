#!coding=utf-8

import threading
import socket
import struct
import os
import numpy
import cv2 as cv
import time
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
     
     
 
def deal_video_data(conn,addr):
    running = Value('i',1)
    yolo_running = Value('i',1)
    task_kill = Value('i',0)
    process_num = 2
    #process_recv = Process(target=recv_video,args=(conn,addr,process_num,running,task_kill))
    
    #process_recv.start()
    recv_video(conn,addr,process_num,running,task_kill)
    
    while running.value:
        pass
    
    yolo_processes = []
    '''
    for i in range(process_num):
        p = Process(target=yolo_video,args=(i,running,task_kill))
        yolo_processes.append(p)
        p.start()
    '''
    '''
    sleepTime = 41
    process_play = Process(target=playVideo,args=(conn,addr,sleepTime,yolo_running,'./yolo/frame/orig1/',task_kill))
    process_play.start()
    
    
    while True:
        e = yolo_processes.__len__()
        for th in yolo_processes:
            if not th.is_alive():
                e -= 1
        if e <= 0:
            yolo_running = 0
            break
        if cv.waitKey(1) == ord('q'):
            task_kill.value = 1
            break
    while process_play.is_alive():
        pass
    '''
    cv.destroyAllWindows()
    
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
    print(task_kill.value)
    while task_kill.value == 0:
        print('aaa')
        length = conn.recv(16) #首先接收来自客户端发送的大小信息        
        if isinstance(length,str) and length:
            print(length)
            l = int(length)
            count += 1
            frames_save_path = "./yolo/frame/orig{}".format(count%pronum)
            stringData = conn.recv(l)
            # 对接收到的内容解码为图片形式
            data = numpy.fromstring(stringData,dtype='uint8')
            decimg = cv.imdecode(data,1)
            cv.imencode('.jpg', decimg)[1].tofile(frames_save_path + "/%.6d.jpg" % count)
            '''
            while data_queue.full():
                time.sleep(5)
                
            data_queue.put(decimg)
            '''    
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
        if not im_dir and not running.value:
            break
        if not im_dir:
            print("空")
            time.sleep(500)
            continue
        count += len(im_dir) - 1
        os.system("./darknet{} detect cfg/yolov3-tiny.cfg yolov3-tiny.weights".format(id))
        os.system("./frame/orig{}/input.txt > rm -rf".format(id))
    print("process {} finish {} images".format(id,count))     
        
    

'''
def frame2video(im_dir,video_dir,fps):
 
    im_list = os.listdir(im_dir)
    #debug
    #os.system("echo $(ls -R ./frame/orig/*.jpg)")
    #print(im_list)
#    im_list.sort(key=lambda x: int(x.replace("frame","").split('.')[0]))  #最好再看看图片顺序对不
    im_list.sort()
    img = Image.open(os.path.join(im_dir,im_list[0]))
    img_size = img.size #获得图片分辨率，im_dir文件夹下的图片分辨率需要一致

    # fourcc = cv2.cv.CV_FOURCC('M','J','P','G') #opencv版本是2
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') #opencv版本是3
    videoWriter = cv2.VideoWriter(video_dir, fourcc, fps, img_size)
    # count = 1
    for i in im_list:
        im_name = os.path.join(im_dir+i)
        frame = cv.imdecode(np.fromfile(im_name, dtype=np.uint8), -1)
        videoWriter.write(frame)
        # count+=1
        # if (count == 200):
        #     print(im_name)
        #     break

    videoWriter.release()
    print('finish')
'''   
def playVideo(conn,addr,sleepTime,yolo_running,im_dir,task_kill):
    q = []
    while not task_kill.value:
        im_list = os.listdir(im_dir)
        if not yolo_running.value and not im_list:
            break   
        im_list.sort()
    
        for i in im_list:
            im_name = os.path.join(im_dir+i)
            np_array = numpy.fromfile(im_name,dtype = numpy.uint8)
            stringData = np_array.tostring()
            frame = cv.imdecode(np_array,-1)
            #conn.send(len(stringData).ljust(16).encode())
            #conn.send(stringData)
            cv.imshow("server",frame)
            q.append(frame)
        
        
        
    print("send back over")    
        
    
    for f in q:
        cv.imshow('server',f)
        if cv.waitKey(sleepTime)==ord('q'):
            break
    

           
        
     
if __name__ == "__main__":
    server = Server()
    server.setup('127.0.0.1',8005)
    server.serverStart(deal_video_data)  
            
