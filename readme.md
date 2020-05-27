<style>
    h1 {
        border-bottom: none
    }
</style>        


### <center><font face="宋体">数据通信大作业</center>

### <center> <font face="宋体">2020 春季</center>

------

# <center><font face="微软雅黑">传输视频的目标识别</center>

------

</br>

</br>

<center>刘国涛   181860055


<center>吴泳锟   181180141


<div STYLE="page-break-after: always;"></div>

</br>

</br>

<p align="right"><font face = "Arial"><font size = 5>CHAPTER</font> <font size = 8>1</p>

</br>

<hr>


<p align="right"><font size = 5>项目概述</p>

<hr>


</br>

### <center>1.1  项目背景

​       基于socket的数据通信是互联网、云计算的技术基础。我们希望使用socket通信实现多客户端与服务端的视频传输，并由服务端返回视频内容的目标识别结果。这个过程可以是离线的，也可以是实时的。

​       这样的交互过程应用场景广泛。可用于公共场所摄像头的实时监控，及时判断危险事件的发生。还可通过云端的视频识别结果生成语音描述，为失明人士“观看“视频提供另一种可能。

</br>

### <center>1.2  预期功能

1. 视频上传（客户端、服务端）

2. 内容识别（服务端）

3. 结果展示（客户端）

   </br>

### <center>1.3  项目规划

<img src="1.png">

</br>

### <center>1.4  分工情况

- 刘国涛
  - 完成视频传输与客户端的结果展示部分
  - 完成服务端目标识别的多进程加速部分
- 吴泳锟
  - 完成图片传输部分
  - 完成服务端yolo目标识别算法的部署

<div STYLE="page-break-after: always;"></div>

</br>

</br>

<p align="right"><font face = "Arial"><font size = 5>CHAPTER</font> <font size = 8>2</p>

</br>

<hr>


<p align="right"><font size = 5>项目实现</p>

<hr>


</br>

### <center>2.1  技术基础

#### <center>2.1.1  socket通信

​       socket，即网络套接字，是不同计算机间进行通信的接口，是工作于网络应用层与传输层之间的一个抽象，如下图。

<img src="2.jpg">

对于基于TCP协议的socket通信，客户端 (Client) 和服务端 (server) 要经历三次握手才能建立连接。

<img src="3.png">

先由客户端发送一个握手包 (SYN) ，第一次握手。服务端有响应后，向客户端发送一个应答包 (SYN, ACK)，第二次握手。客户端再向服务端发送 (ACK) 应答包，第三次握手。至此TCP连接已建立。

​      建立连接后，客户端和服务端可互相发送数据进行通信，通信过程将持续至客户端关闭网络套接字。

</br>

#### <center>2.1.2  yolo目标识别

​       yolo算法是一种基于卷积神经网络 (CNN) 的目标识别算法，其将目标检测问题转换成从图像中提取边界框并计算类别概率的回归问题，网络结构如图。

<img src="yolo.jpg">

​       具体地讲，yolo算法先将输入图片分割成 $s\times s$ 个网格，对每个网格检测中心点落在该格子内的目标，生成一系列边界框及对应的置信度。置信度包含两个方面，一是边界框含有目标的可能性大小，二是这个边界框的准确度。前者的意义是，当边界框包含目标时概率为1，当边界框为背景时概率为0；后者用预测边界框与实际边界框的交并比来衡量。实际上，每个边界框有五个元素：$(x, y, w, h, c)$。其中前四个值表征了边界框的大小与位置，$(x,y)$为框的中心坐标，$(w,h)$是边界框的宽与高。$c$为独热码，有物体则标志为1。通过神经网络的前向传播得到预测值，计算损失函数，并反向传播，最终生成最贴近实际边界框的预测框。

​       实际使用时，可以使用darknet网络框架部署yolo算法，实现过程请参考2.2小节。

#### <center>2.1.3  多进程加速

</br>

</br>

### <center>2.2  具体实现

### </br>

### <center>2.3  成果展示

</br>

### <center>2.4  改进方案

​       由于项目组的资金受限，无法使用并行度更高的GPU单元对目标识别算法进行加速，因而无法实现实时视频的识别与返回。项目组下一步可考虑使用英伟达显卡配合opencv摄像单元对已实现方案进行改进。

<div STYLE="page-break-after: always;"></div>

</br>

</br>

<p align="right"><font face = "Arial"><font size = 5>CHAPTER</font> <font size = 8>3</p>

</br>

<hr>


<p align="right"><font size = 5>项目总结</p>

<hr>
</br>


​       本项目自四月底动工至今，耗时约一个月。项目执行期间，各成员熟悉了python中socket模块的调用，并决定使用将视频拆解成多帧的方案进行传输，同时利用服务端的多进程机制实现目标识别的加速。项目完成后，各成员基本掌握了socket通信的原理，对视频传输并目标识别的实际应用有了更深刻的理解。
