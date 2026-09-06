# 两台 LIMO：有界一手接口审计回执

2026-09-06。NONBALLOT 来源证据记录，不是新科学候选、实验协议、硬件验证结果或放行。按用户最新优先级，主研究为大规模 Lifelong MAPF 纯仿真；此核验止于可选实物补充的接口证据，不扩展双车系统搭建。全部保护参数未赋值；未实现、构建、测试、仿真、连接/控制实物或生成载荷。

实际子任务 /root/limo_interface_evidence 已返回非空完整最终消息，root 完整阅读。下文是其来源回执的整理和根核验，不冒称逐字转录。该任务不使用任何 skill、不读本地科学工件、不写文件；只取得官方仓库以下两个精确文件，没有目录扫描或读取其他源码。匿名 API 一次限流失败后经现有 GitHub CLI 认证成功，失败不计证据。它不是原 69E1 MAPF 全源码任务的副本。

## 固定对象及阅读强度

官方 https://github.com/agilexrobotics/limo_ros ，GitHub ref API 固定 master commit 为 4c78efc674cfc154012fe851fbda89c50be5b983。此版本并未被证明就是用户两台车实际安装的版本。

| 精确文件 | Git blob | SHA256 | bytes / 完整源行数 | 本次实际阅读 |
|---|---|---|---|---|
| limo_base/src/limo_driver.cpp | 2762add895201801c8d73f8f40d32b68fcf629a4 | 3888c8d46ae03397fc146ec53214997210483f238c881dab352813c309aa2d38 | 19852 / 580 | 代理一次完整读取 L1–580，核 Git blob 和 size；root 另取同固定对象核同身份，合并输出截断处用该次缓存补 L1–50 及 L51，完整覆盖 L1–580 至 SOURCE-READ-END |
| limo_base/msg/LimoStatus.msg | 064f26853ed2498ecd5530726c61ffd13b33ded2 | 1eea5888c426d99f5becd740c9ed4fd66456f7a473d53199de51e9ed91c4f47d | 114 / 7 | 代理完整读取 L1–7 并核散列；root 后用同固定 Contents API 独立核 blob/size 并读完七行，未另算消息 SHA256 |

代理所读 Contents API 完整响应分别 28466 和 1259 bytes，两个源文件末尾都有换行。root 驱动读取第一次因沙箱 socket 禁止失败，确认错误后同命令正常升级权限成功；没有通过其他路径绕过权限，没有从失败输出推断源码行为。

## 与研究有关的实际事实

1. [驱动 L46–49、L320–400](https://github.com/agilexrobotics/limo_ros/blob/4c78efc674cfc154012fe851fbda89c50be5b983/limo_base/src/limo_driver.cpp#L320-L400)：Twist 经不同底盘模式的转换进入 setMotionCommand，编码后由 sendFrame 写串口。能发命令不意味着动作已经开始或完成；这一路没有动作级因果确认。
2. [L169–183、L226–231、L453–541](https://github.com/agilexrobotics/limo_ros/blob/4c78efc674cfc154012fe851fbda89c50be5b983/limo_base/src/limo_driver.cpp#L453-L541)：odom 位置使用反馈速度、IMU 派生方向和接收时间差在主机积分。另一个轮计数分支只解析局部变量，没有在本文件用于该位置积分。底盘速度反馈的固件来源未读，不能提升为已核实的地面位移真值。
3. [L233–253、L402–450](https://github.com/agilexrobotics/limo_ros/blob/4c78efc674cfc154012fe851fbda89c50be5b983/limo_base/src/limo_driver.cpp#L402-L450)：IMU 消息组合不同帧更新的缓存，由欧拉角帧触发发布，四元数仅使用 yaw；里程计航向有增量处理。源码内固定协方差不是现场标定结果，也不是确定性的误差上界。
4. [L111–115、L504–521、L544–554](https://github.com/agilexrobotics/limo_ros/blob/4c78efc674cfc154012fe851fbda89c50be5b983/limo_base/src/limo_driver.cpp#L111-L115)：frame.stamp 是主机读取帧头时的 ROS 时刻；IMU/状态用该值，odom 和 TF 又用发布侧当前时刻。不能直接把它当底盘采样或物理完成时刻；已读路径没有提供跨车时钟同步或通信延迟上界。
5. [完整 LimoStatus.msg](https://github.com/agilexrobotics/limo_ros/blob/4c78efc674cfc154012fe851fbda89c50be5b983/limo_base/msg/LimoStatus.msg) 只有 Header、vehicle_state、control_mode、battery_voltage、error_code、motion_mode。驱动的对应发布没有绑定 MOVE/tid/冲突区/终点判据。普通状态反馈不能当资源清空或任务完成证书；只依据这两个文件，尚无所需的动作级证据链。
6. [L260–284、L340–389](https://github.com/agilexrobotics/limo_ros/blob/4c78efc674cfc154012fe851fbda89c50be5b983/limo_base/src/limo_driver.cpp#L340-L389)：错误处理主要输出日志，发送函数没有把串口写入与物理完成匹配。阿克曼分支直接取线速度/角速度比，未见全零指令专用分支；这提示需核实际模式和依赖，不能据此泛化为所有车辆不能停车，也不能从下发零速证明模型要求的无滞后精确驻停。

## 解释与未读依赖

上述接口可以成为未来记录命令、反馈与主机时刻的入口。若现场另有经过核验的位置参考、坐标和车体区域定义、时间对齐及测量不确定性说明，两台车有机会量化局部交接与等待的效应。odom 参考点到达目标不是整个车体已清空，文档中的导航功能也不是实际安装、运行或误差界证据。现无实物轨迹、性能或制动结果，不推定双车已建立共同坐标，也不推定尚未建立。

未读依赖包括驱动头文件与参数初值、串口实现、底层协议/固件、实车软硬件/固件版本及启动配置、定位链路、现场参考与日志。因此结论限定为“这两个文件不足以单独证明所需可信接口”，不能推断整个仓库/平台不可能实现它。厂商示例和源码数字均未变成保护参数值或实验配置。可选实物证据不能代替大规模仿真的吞吐、失败、总处理开销和扩展性比较。

实际完整回执已收到并保存此可追踪整理，来源证据不作正式审查票；如用于后继候选的实质假设或协议，随新固定候选接受已约定顺序审查。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。
