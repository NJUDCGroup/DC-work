#!coding=utf-8
 
import socket
import os
import sys
import struct

def socket_client():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 9001))
    except socket.error as msg:
        print (msg)
        sys.exit(1)
    print (s.recv(1024))

    # 需要传输的文件路径
    filepath = raw_input('Please input an image for object detection:\n')
    print (filepath)
    # 判断是否为文件
    if os.path.isfile(filepath):
        # 定义定义文件信息。128s表示文件名为128bytes长，l表示一个int或log文件类型，在此为文件大小
        fileinfo_size = struct.calcsize('128sl')
        # 定义文件头信息，包含文件名和文件大小
        fhead = struct.pack('128sl', os.path.basename(filepath).encode('utf-8'), os.stat(filepath).st_size)
        # 发送文件名称与文件大小
        s.send(fhead)

        # 将传输文件以二进制的形式分多次上传至服务器
        fp = open(filepath, 'rb')
        while 1:
            data = fp.read(1024)
            if not data:
                print ('{0} file send over...'.format(os.path.basename(filepath)))
                break
            s.send(data)

            
        buf = s.recv(fileinfo_size)
        # 判断是否接收到文件头信息
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
                    data = s.recv(1024)
                    recvd_size += len(data)
                else:
                    data = s.recv(filesize - recvd_size)
                    recvd_size = filesize
                fp.write(data)
            fp.close()
            
            
        # 关闭当期的套接字对象
        s.close()
        
if __name__ == '__main__':
    socket_client()

