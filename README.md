# spill-detection
核心功能为抛洒物检测。

## 1. 数据说明
**数据来源**: 金科院
<br>
**数据场景**: 南京高速
<br>
**路段长度**: 约400m
<br>
**采集设备**: 雷达
<br>
**帧率**: 20FPS
<br>
**开始时间戳**: 2023-10-20 10:03:41.883
<br>
**开始帧数**: 62748

### 数据格式
离线模拟场景: 从txt文件读取接受
<br>
每帧传来数据为list, list元素为代表目标信息的dict, 即: 
<br>
第n帧:  [car1, car2, ...]
<br>
各car目标的dict形式为: 
<br>
TargetId | XDecx | YDecy | ZDecz | VDecVx | VDecVy | Xsize | Ysize | TargetType | Longitude | Latitude | Confidence | EventType | LineNum | Frame
<br>
TargetType, EventType的数据内容与对应类别, 可在go的转码代码中找到。
``
	var clsMap = map[int8]string{
	0: "未定义目标",
	1: "小车",
	2: "大车",
	3: "摩托",
	4: "自行车",
	5: "行人",
}

var eventMap = map[uint8]string{
	1:  "逆行",
	2:  "大车超高速",
	3:  "小车超高速",
	4:  "大车超低速",
	5:  "小车超低速",
	6:  "停车",
	7:  "占用应急车道行驶",
	8:  "压线",
	9:  "变道",
	10: "占用应急车道停车",
	11: "占用应急车道逆行",
}

func unifiedEventType(eventType uint8) string {
	switch eventType {
	case 1, 11:
		return "机动车逆行"
	case 2, 3:
		return "机动车超速"
	case 4, 5:
		return "机动车低速"
	case 6, 10:
		return "机动车驶停"
	case 7:
		return "占用应急车道行驶" // 特有事件
	case 8:
		return "压线" // 特有事件
	case 9:
		return "变道" // 特有事件
	default:
		return "未知"
	}
}
``

#### 数据传输格式
参见文档<a href="./docs/data_format.txt" >数据格式</a>

#### 数据内容说明
**targetType**: 0-未定义目标, 1-小车, 2-大车, 3-摩托, 4-自行车, 5-行人

**距离单位**: m

**速度单位**: m/s

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