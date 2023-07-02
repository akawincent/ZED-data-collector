# :camera_flash: ZED data collector 

> 本项目使用ZED2相机制作数据集以评估视觉里程计的精度和鲁棒性，数据集中收集了左右相机图像、相机内参、时间戳、轨迹真值

### 1. 工程依赖

本项目是在**Windows10 64-bit**系统上运行的

- **Python**：使用Python作为开发相机功能的编程语言，版本为**3.10.2**

- **Numpy**：使用Numpy管理数据，版本为**1.22.2**

- **OpenCV**：OpenCV用来进行基本的图像显示与存储，版本为**4.5.5.62**
- **OpenGL**：OpenGL用来对位姿跟踪过程中对相机位姿和轨迹进行三维可视化，版本为**3.1.6**

- **ZED SDK**：获取使用和开发ZED相机所需的API，版本为**3.8**

- **Cuda,Cudnn**：调用GPU的并行计算功能，加速运行ZED相机的深度感知，Cuda的版本为**10.2**，Cudnn的版本为**8.7.0**

### 2. 功能介绍

本项目录制数据集时提供**实时录制**和**离线录制**两种模式。

##### 2.1 实时录制模式

在实时录制模式中，ZED相机通过`grab()`读入视频流的图像后，顺序执行以下计算量较大花费时间较多的功能：保存图像到硬盘、位姿估计***、***轨迹三维可视化。只有在上述功能执行完成后，ZED相机才会实时的继续读入视频流中的下一帧图像，然而在经过大计算量的处理后，实际上`grab()`读入的下一帧已经是相机拍摄到的往后几帧的图像，这就造成了掉帧。因此尽管设置了相机初始帧率参数为60FPS,在图像分辨率为`672*376`，保存格式为`JPEG`格式时，录制的数据集实际图像帧率只能达到`12FPS`。

##### 2.2 离线录制模式

ZED相机支持录制SVO格式视频，SVO格式视频中不仅包含了图像信息，还可以从中提取出时间戳、轨迹真值等信息。因此可以选择先录制SVO视频而不做处理，随后再从这个视频中离线导出所需要的数据。这样就可以避免实时录制模式中掉帧的缺点。设置参数以60FPS录制SVO视频，在图像分辨率为`1280*720`，保存格式为`PNG`格式时，导出的数据集图像帧率可以达到`60FPS`。

### 3. 使用指南

##### 3.1 运行实时录制模式

运行下面的指令以运行实时录制模式：

```powershell
cd .\Realtime
python main.py
```

##### 3.2 运行离线录制模式

首先运行下面的指令以录制SVO视频，需要传入录制文件名参数

```powershell
cd .\SVO
python record.py 1.svo
```

`playback.py`可以将录制的视频回放，需要传入文件名参数

```powershell
python playback.py 1.svo
```

最终运行`export.py`程序导出数据

```powershell
python export.py
```

##### 3.3 数据集

生成的相关数据文件如下：

- 左右图像文件`images`，图像文件以时间戳命名

- 相机内参文件`calib_stero.txt`

```
Pinhole fx fy cx cy 0
height width
crop
height width
baseline
```

- 时间戳文件`times.txt`

```
timestamp(microsecond)
```

- 轨迹真值文件`groundtruth.tum`

```
timestamp t_x t_y t_z q_x q_y q_z q_w
```

### 4. 文件架构

##### 4.1 Realtime

```
│  main.py: 实时录制功能的主程序
│  path.py: 提供文件路径
│  record.py: 封装了保存图像、保存相机内参、保存时间戳以及轨迹真值文件的函数
│  utils.py: 提供了坐标变换、图像显示等基本函数
├─ data
│  │  calib_stereo.txt: 相机内参文件
│  │  groundtruth.tum: 轨迹真值文件
│  │  times.txt: 时间戳文件
│  └─ images
│      ├─ image_0: 左目图像
│      └─ image_1: 右目图像
├─ ogl_viewer
│  │  tracking_viewer.py: 三维可视化相机位姿和运动轨迹
│  │  zed_model.py: 模型文件
│  └─ __pycache__: 缓存文件
└─ __pycache__: 缓存文件

```

##### 4.2 SVO

```
│  1.svo: 测试视频文件
│  export.py: 离线导出SVO视频中包含的信息，包含左右图像、时间戳
│  path.py: 提供文件路径
│  playback.py: 回放SVO视频
│  record.py: 录制SVO视频
├─ data
│  │  calib_stereo.txt: 相机内参文件
│  │  groundtruth.tum: 轨迹真值文件
│  │  times.txt: 时间戳文件
│  └─ images
│      ├─ image_0: 左目图像
│      └─ image_1: 右目图像
└─ __pycache__: 缓存文件
```

### 5. 参考资料

[stereolabs/zed-sdk: ⚡️The spatial perception framework for rapidly building smart robots and spaces (github.com)](https://github.com/stereolabs/zed-sdk)

[stereolabs/zed-python-api: Python API for the ZED SDK (github.com)](https://github.com/stereolabs/zed-python-api)

[Python API Documentation | Python API Reference | Stereolabs](https://www.stereolabs.com/docs/api/python/)

[Stereolabs Docs: API Reference, Tutorials, and Integration](https://www.stereolabs.com/docs/)