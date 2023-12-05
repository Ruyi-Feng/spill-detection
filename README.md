# spill-detection
核心功能为抛洒物检测。

## 1. 数据说明
**数据来源**：金科院
<br>
**数据场景**: 南京高速
<br>
**路段长度**：约400m
<br>
**采集设备**: 雷达
<br>
**帧率**：20FPS
<br>
**开始时间戳**:2023-10-20 10:03:41.883
<br>
**开始帧数**:62748
### 数据格式
离线模拟场景：从txt文件读取接受
<br>
每帧传来数据为list，list元素为代表目标信息的dict，即：
<br>
第n帧： [car1, car2, ...]
<br>
各car目标的dict形式为：
<br>
TargetId | XDecx | YDecy | ZDecz | VDecVx | VDecVy | Xsize | Ysize | TargetType | Longitude | Latitude | Confidence | EventType | LineNum | Frame

## 2. 思维导图
<p>
<img
src="./docs/mindMap/framework.png"
alt="项目框架"
title="项目框架"
width="100%"
>
</p>

## 3. 算法逻辑

<p>
<img
src="./docs/algorithms_logic.png"
alt="算法逻辑"
title="算法逻辑"
width="100%"
>
</p>
