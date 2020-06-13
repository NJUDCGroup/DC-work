现已完成视频目标识别，但是没有把socket通信传输视频加入进去

有几点需要注意：

1、由于yolo中的video2frame.py，通信的时候最好要把client、server分成两个文件夹放，且传输视频目标地址一定要和server.py相同

2、video2frame.py默认将输入视频名称视为test.mp4

2、video2frame.py将所有帧存入yolo/frame/orig并生成input.txt文件记录所有帧，之后调用yolo/.darknet神经网络对输入的input.txt进行识别，识别后的所有帧存在yolo/frame/pred，最后再调用frame2video.py生成pred.mp4



测试方法：

在yolo文件夹中运行test.py，即可得到pred.mp4