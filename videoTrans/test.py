from multiprocessing import Process
import os
def server_start():
    os.system("python server.py")
def client_start():
    os.system("python client.py")
    
s = Process(target=server_start)
c = Process(target=client_start)
s.start()
c.start()