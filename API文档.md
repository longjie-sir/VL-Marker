# AI 视觉智能监控 API 中台系统 - API文档

## 1. 概述

本系统提供了两个核心RESTful API，用于站点配置和违规检测。

## 2. 接口列表

| 路径 | 方法 | 功能描述 |
| :--- | :--- | :--- |
| `/api/v1/sites/config` | `POST` | 注册/更新站点配置 |
| `/api/v1/analyze/frame` | `POST` | 执行单帧图片违规检测 |

## 3. 站点配置接口

### 3.1 路径

`POST /api/v1/sites/config`

### 3.2 功能

前端完成画框后，提交区域坐标，用于注册或更新站点配置。

### 3.3 请求体 (JSON)

```json
{
  "site_id": "wh_gate_01",
  "site_name": "一号仓库大门",
  "rule_type": "in_bounds",
  "polygon_cfg": [
    {"x": 0.15, "y": 0.20},
    {"x": 0.85, "y": 0.20},
    {"x": 0.90, "y": 0.80},
    {"x": 0.10, "y": 0.80}
  ]
}
```

**参数说明**：
- `site_id`：站点唯一标识符，字符串类型
- `site_name`：站点业务名称，字符串类型
- `rule_type`：规则类型，字符串类型，可选值：`in_bounds` (必须在框内) / `no_entry` (禁止入内)，默认为 `in_bounds`
- `polygon_cfg`：多边形顶点的相对坐标数组，至少包含3个点，每个点包含 `x` 和 `y` 两个字段，值范围为 0.0 ~ 1.0

### 3.4 响应体 (JSON)

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "site_id": "wh_gate_01",
    "site_name": "一号仓库大门",
    "rule_type": "in_bounds",
    "polygon_cfg": [
      {"x": 0.15, "y": 0.2},
      {"x": 0.85, "y": 0.2},
      {"x": 0.9, "y": 0.8},
      {"x": 0.1, "y": 0.8}
    ]
  }
}
```

**响应说明**：
- `code`：响应状态码，200 表示成功
- `message`：响应消息，成功时为 "success"
- `data`：响应数据，包含保存的站点配置信息

## 4. 推理接口

### 4.1 路径

`POST /api/v1/analyze/frame`

### 4.2 功能

上游系统传入图片，系统返回是否有违规行为。

### 4.3 请求体 (JSON)

```json
{
  "site_id": "wh_gate_01",
  "image_base64": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAY..."
}
```

**参数说明**：
- `site_id`：站点唯一标识符，字符串类型
- `image_base64`：Base64编码的图片，字符串类型

### 4.4 响应体 (JSON)

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "site_id": "wh_gate_01",
    "has_violation": true,
    "violation_desc": "检测到一辆白色货车车轮已超出红色合法区域边界。",
    "model_latency_ms": 2350
  }
}
```

**响应说明**：
- `code`：响应状态码，200 表示成功
- `message`：响应消息，成功时为 "success"
- `data`：响应数据，包含以下字段：
  - `site_id`：站点唯一标识符
  - `has_violation`：是否有违规行为，布尔值
  - `violation_desc`：违规描述，字符串类型
  - `model_latency_ms`：模型调用延迟，毫秒

## 5. 错误处理

系统在遇到错误时会返回相应的错误码和错误消息，例如：

```json
{
  "detail": "站点 wh_gate_02 不存在"
}
```

常见错误：
- 404：站点不存在
- 400：请求参数无效
- 500：服务器内部错误

## 6. 示例代码

### 6.1 注册站点配置

```python
import requests

url = "http://localhost:8000/api/v1/sites/config"
payload = {
    "site_id": "wh_gate_01",
    "site_name": "一号仓库大门",
    "rule_type": "in_bounds",
    "polygon_cfg": [
        {"x": 0.15, "y": 0.20},
        {"x": 0.85, "y": 0.20},
        {"x": 0.90, "y": 0.80},
        {"x": 0.10, "y": 0.80}
    ]
}

response = requests.post(url, json=payload)
print(response.json())
```

### 6.2 执行违规检测

```python
import requests
import base64
from PIL import Image
from io import BytesIO

# 加载图片并编码为Base64
image = Image.open("test.jpg")
buffer = BytesIO()
image.save(buffer, format="JPEG")
image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

url = "http://localhost:8000/api/v1/analyze/frame"
payload = {
    "site_id": "wh_gate_01",
    "image_base64": image_base64
}

response = requests.post(url, json=payload)
print(response.json())
```