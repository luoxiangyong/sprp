# sprp
A simple photogrammetry route planner.

 This package is tested on python3.

## 基本介绍
基于公式：

$$\frac{focusLength}{flightHeight} = \frac{pixelSize}{GSD}$$

(其中，$focusLength$为相机焦距，$flightHeight$为飞行高度，$pixelSize$为像素点物理大小，
$GSD$为地面分辨率)。


提供以下几种类型的航摄区域的自动曝光点生成:

    - 简单线性
    - 条带
    - 多边形区域
  
成果包含：根据航向、旁向重叠度自动生成的曝光点、每个曝光点对应的footprint、每条航线等geometry
类型。

支持以下特性：

    - 可导出shaplefile文件，各种geometry分别存储
    - 可导出ply文件，便于三维展示
    - 可导出las文件，便于三维展示，需要安装pylas库
    - 可导出简单txt文件，只包含每个曝光点的x,y,z坐标和点号
    - 可导出QGIS的memery类型矢量，便于直接与QGIS交互
    - 可导出GeoJson
    - 支持基于Flask和Leaflet的Web端交互自动设计

以下是简单的成果展示：

- QGIS Memory文件

![QGIS Memory文件](https://github.com/luoxiangyong/sprp/blob/master/images/qgis-memory-demo.png)

- PLY文件

![PLY文件](https://github.com/luoxiangyong/sprp/blob/master/images/ply-demo.png)

## 简单使用

### 安装
```python
pip3 install sprp
```
### 使用
```python
from sprp.core.alg import *
from sprp.export.txt import *

ssc = SimpleStripCalculator(116.23589,39.90387,116.25291,39.90391,
        3,2, 
        **{
        "cameraWidth": 4000,
        "cameraHeight":3000,
        "focusLength":35,
        "pixelSize":2,
        "gsd":0.05,
        "flightSpeed":80,
        "courseOverlap":0.8,
        "sidewiseOverlap":0.6, 
    })

result = ssc.calculate()
print(result)

sfe = TxtExporter('/path/to/save/test-data/test-txt.txt')
sfe.save(ssc)
```

## 开发

请按以下步骤准备你的开发环境。

1. 下载代码

```bash
git clone https://github.com/luoxiangyong/sprp.git
```

2. 准备虚拟环境

   ```python
   cd sprp
   python3 -m venv venv
   source ./venv/bin/activate
   ```

3. 安装开发依赖

   ```python
   pip3 -r requirements-dev.txt
   pip3 install -e .
   ```

   