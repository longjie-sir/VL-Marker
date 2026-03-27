# AI 视觉智能监控 API 中台系统 - 部署指南

## 目录

1. [项目概述](#1-项目概述)
2. [技术架构](#2-技术架构)
3. [环境要求](#3-环境要求)
4. [安装部署](#4-安装部署)
5. [API接口文档](#5-api接口文档)
6. [配置说明](#6-配置说明)
7. [生产部署](#7-生产部署)
8. [使用示例](#8-使用示例)
9. [常见问题](#9-常见问题)
10. [维护与监控](#10-维护与监控)
11. [项目结构](#11-项目结构)

***

## 1. 项目概述

### 1.1 项目简介

**AI 视觉智能监控 API 中台系统** 是一个轻量级、SaaS化、控制面与数据面解耦的AI视觉监控API中台系统。该系统基于阿里云Qwen-VL视觉大模型，提供智能化的视频监控违规检测能力。
<br />
<br />
**项目的构建需求来源是** ：因为项目紧急的需要，需提供一个可以对视频信息进行分析的算法，需要对视频中的给定区域进行监控，如果有车辆驶入，需要能告警，但是项目本身没有什么高端硬件，就是平常的CPU虚拟机，加上人手（没人）和时间（两天）原因就快速的搭建了这个项目。项目本身存在诸多使用场景限制，首先调用了云端的视觉大模型，其次仅针对定向摄像头（一个方位，不考虑摄像头移动）。
基于以上要求，因为仅有两天的时间，因此就构想了使用视觉大模型来解决这个问题，项目提供后台，可以先对视频中的某一帧图像进行相关区域的划分，然后可以通过接入视频流、抽取视频帧的方式进行问答，本项目在开发之处是使用了“车辆驶入告警”这一案例进行的测试、分析。当然，实际的场景还有很多，可以根据prompt的方式去驱动分析。在“video”文件夹中放置了测试用的视频，在实际使用过程中需要自己实现视频流的接入，并且进行抽帧（抽帧间隔最好不要小于5秒，因为要考虑到AI的输出效率）。
系统提供了两个模块：“站点管理”和“视频分析”，“视频分析”模块仅是为了测试所用，真正使用中，该模块实际是在项目上去实现，然后调用本项目提供的分析接口。
<img width="1510" height="690" alt="Snipaste_2026-03-27_10-16-42" src="https://github.com/user-attachments/assets/1c6f261d-2c2c-43de-84e0-914ad717f13e" />

<br />

### 1.2 核心功能

| 功能模块        | 功能描述                                          |
| ----------- | --------------------------------------------- |
| **站点配置管理**  | 支持多站点配置，每个站点可独立设置监控区域和检测规则                    |
| **多边形区域标记** | 通过前端界面绘制多边形区域，标记监控范围                          |
| **违规检测规则**  | 支持两种检测规则：`in_bounds`（必须在框内）和 `no_entry`（禁止入内） |
| **视频帧分析**   | 对视频帧进行智能分析，检测车辆是否违规                           |
| **AI智能分析**  | 基于阿里云Qwen-VL视觉大模型，提供高精度的违规检测                  |
<img width="2436" height="1289" alt="Snipaste_2026-03-27_10-15-44" src="https://github.com/user-attachments/assets/11c4009d-910a-42fc-aeed-fcb589c52247" />
<img width="1500" height="1568" alt="Snipaste_2026-03-27_12-09-21" src="https://github.com/user-attachments/assets/71230c07-92f2-47c9-bf23-fa27dd079199" />
### 1.3 技术特点

- **前后端分离架构**：后端提供RESTful API，前端使用Vue 3构建
- **轻量级数据库**：使用SQLite数据库，无需额外安装数据库服务
- **多边形区域可视化**：将监控区域以透明红色填充的方式绘制在图片上
- **灵活的Prompt配置**：支持自定义分析提示词，满足不同场景需求
- **跨域支持**：内置CORS中间件，支持跨域请求

***

## 2. 技术架构

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (Vue 3)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  站点管理    │  │  视频分析    │  │  结果展示    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     后端 (FastAPI)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  站点API     │  │  分析API     │  │  图像处理    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   SQLite    │    │  OpenCV     │    │  DashScope  │
│   数据库     │    │  图像处理    │    │  AI服务     │
└─────────────┘    └─────────────┘    └─────────────┘
```

### 2.2 后端技术栈

| 技术            | 版本     | 用途         |
| ------------- | ------ | ---------- |
| **Python**    | 3.10+  | 编程语言       |
| **FastAPI**   | latest | 高性能Web框架   |
| **SQLModel**  | latest | ORM框架      |
| **SQLite**    | -      | 轻量级数据库     |
| **OpenCV**    | latest | 图像处理库      |
| **Pillow**    | latest | 图像处理库      |
| **DashScope** | latest | 阿里云AI服务SDK |
| **Uvicorn**   | latest | ASGI服务器    |

### 2.3 前端技术栈

| 技术             | 版本  | 用途                |
| -------------- | --- | ----------------- |
| **Vue**        | 3.x | 渐进式JavaScript框架   |
| **TypeScript** | 5.x | 类型安全的JavaScript超集 |
| **Vite**       | 5.x | 下一代前端构建工具         |

### 2.4 AI模型

| 模型               | 提供商 | 用途                  |
| ---------------- | --- | ------------------- |
| **Qwen-VL-Plus** | 阿里云 | 视觉语言大模型，用于图像理解和违规检测 |

***

## 3. 环境要求

### 3.1 后端环境

| 环境         | 要求                        |
| ---------- | ------------------------- |
| **Python** | 3.10 或更高版本                |
| **操作系统**   | Windows / Linux / macOS   |
| **网络**     | 需要网络连接以调用阿里云DashScope API |
| **内存**     | 建议 2GB+                   |
| **磁盘**     | 建议 1GB+ 可用空间              |

### 3.2 前端环境（开发模式）

| 环境          | 要求         |
| ----------- | ---------- |
| **Node.js** | 16.x 或更高版本 |
| **npm**     | 8.x 或更高版本  |

### 3.3 阿里云DashScope API

- 需要有效的阿里云账号
- 需要开通DashScope服务
- 需要获取API Key

***

## 4. 安装部署

### 4.1 后端部署

#### 4.1.1 克隆项目

```bash
git clone <项目地址>
cd VL-Marker
```

#### 4.1.2 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 4.1.3 安装依赖

```bash
pip install -r requirements.txt
```

#### 4.1.4 配置环境变量

在项目根目录创建 `.env` 文件：

```env
# 阿里云DashScope API密钥
DASHSCOPE_API_KEY=your_api_key_here
```

> **重要**：将 `your_api_key_here` 替换为您的阿里云DashScope API密钥。

#### 4.1.5 启动服务

**开发模式（支持热重载）**：

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

**生产模式**：

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

服务启动后，可以访问以下地址：

- API服务：<http://localhost:8001>
- API文档（Swagger UI）：<http://localhost:8001/docs>
- API文档（ReDoc）：<http://localhost:8001/redoc>

### 4.2 前端部署

#### 4.2.1 进入前端目录

```bash
cd frontend
```

#### 4.2.2 安装依赖

```bash
npm install
```

#### 4.2.3 配置API地址

编辑 `frontend/src/services/api.ts`，修改API基础URL：

```typescript
const API_BASE_URL = 'http://localhost:8001/api/v1';
```

> **生产环境**：将URL改为实际的后端服务地址。

#### 4.2.4 开发模式启动

```bash
npm run dev
```

#### 4.2.5 构建生产版本

```bash
npm run build
```

构建完成后，静态文件将生成在 `frontend/dist` 目录下。

#### 4.2.6 部署静态文件

将 `frontend/dist` 目录下的所有文件部署到Web服务器（如Nginx、Apache等）。

***

## 5. API接口文档

### 5.1 接口概览

| 接口路径                      | 方法   | 功能描述       |
| ------------------------- | ---- | ---------- |
| `/api/v1/sites/config`    | POST | 注册/更新站点配置  |
| `/api/v1/sites/{site_id}` | GET  | 获取指定站点配置   |
| `/api/v1/sites`           | GET  | 获取所有站点配置   |
| `/api/v1/analyze/frame`   | POST | 执行单帧图片违规检测 |

### 5.2 站点配置接口

#### 5.2.1 注册/更新站点配置

**请求**：

```
POST /api/v1/sites/config
Content-Type: application/json
```

**请求体**：

```json
{
  "site_id": "js01",
  "site_name": "江苏一号仓库大门",
  "rule_type": "in_bounds",
  "polygon_cfg": [
    {"x": 0.15, "y": 0.20},
    {"x": 0.85, "y": 0.20},
    {"x": 0.90, "y": 0.80},
    {"x": 0.10, "y": 0.80}
  ],
  "reference_image": "",
  "prompt": "请检查图片中是否有车驶入标记的红色区域内，并严格遵守以下json格式进行信息的返回:{\"result\":true/false,\"reason\":\"判断理由\"}"
}
```

**参数说明**：

| 参数                | 类型     | 必填 | 说明                                                       |
| ----------------- | ------ | -- | -------------------------------------------------------- |
| `site_id`         | string | 是  | 站点唯一标识符                                                  |
| `site_name`       | string | 是  | 站点业务名称                                                   |
| `rule_type`       | string | 否  | 规则类型：`in_bounds`（必须在框内）/ `no_entry`（禁止入内），默认 `in_bounds` |
| `polygon_cfg`     | array  | 是  | 多边形顶点坐标数组，至少3个点，坐标为相对值（0.0-1.0）                          |
| `reference_image` | string | 否  | 参考图片的Base64编码                                            |
| `prompt`          | string | 否  | 分析提示词，支持占位符 `{rule_type}`                                |

**响应体**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "site_id": "js01",
    "site_name": "江苏一号仓库大门",
    "rule_type": "in_bounds",
    "polygon_cfg": [
      {"x": 0.15, "y": 0.2},
      {"x": 0.85, "y": 0.2},
      {"x": 0.9, "y": 0.8},
      {"x": 0.1, "y": 0.8}
    ],
    "reference_image": "",
    "prompt": "请检查图片中是否有车驶入标记的红色区域内..."
  }
}
```

#### 5.2.2 获取指定站点配置

**请求**：

```
GET /api/v1/sites/{site_id}
```

**响应体**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "site_id": "js01",
    "site_name": "江苏一号仓库大门",
    "rule_type": "in_bounds",
    "polygon_cfg": [...],
    "reference_image": "",
    "prompt": "..."
  }
}
```

#### 5.2.3 获取所有站点配置

**请求**：

```
GET /api/v1/sites
```

**响应体**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "sites": [
      {
        "site_id": "js01",
        "site_name": "江苏一号仓库大门",
        "rule_type": "in_bounds",
        "polygon_cfg": [...],
        "reference_image": "",
        "prompt": "...",
        "created_at": "2024-01-01 12:00:00"
      }
    ]
  }
}
```

### 5.3 违规检测接口

#### 5.3.1 执行单帧图片违规检测

**请求**：

```
POST /api/v1/analyze/frame
Content-Type: application/json
```

**请求体**：

```json
{
  "site_id": "js01",
  "image_base64": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAY..."
}
```

**参数说明**：

| 参数             | 类型     | 必填 | 说明          |
| -------------- | ------ | -- | ----------- |
| `site_id`      | string | 是  | 站点唯一标识符     |
| `image_base64` | string | 是  | Base64编码的图片 |

**响应体**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "site_id": "js01",
    "has_violation": true,
    "violation_desc": "检测到一辆白色货车车轮已超出红色合法区域边界。",
    "model_latency_ms": 2350
  }
}
```

**响应字段说明**：

| 字段                 | 类型      | 说明         |
| ------------------ | ------- | ---------- |
| `site_id`          | string  | 站点唯一标识符    |
| `has_violation`    | boolean | 是否存在违规行为   |
| `violation_desc`   | string  | 违规描述信息     |
| `model_latency_ms` | number  | 模型调用耗时（毫秒） |

***

## 6. 配置说明

### 6.1 环境变量配置

在项目根目录的 `.env` 文件中配置：

```env
# 阿里云DashScope API密钥（必填）
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 6.2 前端API地址配置

编辑 `frontend/src/services/api.ts`：

```typescript
// 开发环境
const API_BASE_URL = 'http://localhost:8001/api/v1';

// 生产环境
const API_BASE_URL = 'https://your-domain.com/api/v1';
```

### 6.3 服务端口配置

编辑 `main.py` 修改默认端口：

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # 修改端口号
```

### 6.4 CORS配置

编辑 `main.py` 修改CORS设置：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

***

## 7. 生产部署

### 7.1 使用Docker部署

#### 7.1.1 创建Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 8001

# 启动命令
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### 7.1.2 构建镜像

```bash
docker build -t vl-marker:latest .
```

#### 7.1.3 运行容器

```bash
docker run -d \
  --name vl-marker \
  -p 8001:8001 \
  -e DASHSCOPE_API_KEY=your_api_key_here \
  vl-marker:latest
```

### 7.2 Nginx配置

#### 7.2.1 后端代理配置

```nginx
server {
    listen 80;
    server_name api.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 增加超时时间（AI模型响应可能较慢）
        proxy_read_timeout 60s;
    }
}
```

#### 7.2.2 前端静态文件配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /var/www/vl-marker/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 60s;
    }
}
```

### 7.3 HTTPS配置

使用Let's Encrypt免费证书：

```bash
# 安装Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 7.4 性能优化建议

1. **使用Gunicorn多进程模式**：

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001
```

1. **启用响应压缩**：

```python
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

1. **数据库优化**：
   - 定期清理过期数据
   - 添加适当的索引

***

## 8. 使用示例

### 8.1 完整工作流程

```
1. 配置站点 → 2. 上传视频帧 → 3. 获取检测结果 → 4. 处理检测结果
```

### 8.2 Python示例代码

#### 8.2.1 注册站点配置

```python
import requests

url = "http://localhost:8001/api/v1/sites/config"
payload = {
    "site_id": "js01",
    "site_name": "江苏一号仓库大门",
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

#### 8.2.2 执行违规检测

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

url = "http://localhost:8001/api/v1/analyze/frame"
payload = {
    "site_id": "js01",
    "image_base64": image_base64
}

response = requests.post(url, json=payload)
result = response.json()

if result["data"]["has_violation"]:
    print(f"检测到违规: {result['data']['violation_desc']}")
else:
    print("未检测到违规")
```

### 8.3 cURL示例

#### 8.3.1 注册站点

```bash
curl -X POST "http://localhost:8001/api/v1/sites/config" \
  -H "Content-Type: application/json" \
  -d '{
    "site_id": "js01",
    "site_name": "江苏一号仓库大门",
    "rule_type": "in_bounds",
    "polygon_cfg": [
      {"x": 0.15, "y": 0.20},
      {"x": 0.85, "y": 0.20},
      {"x": 0.90, "y": 0.80},
      {"x": 0.10, "y": 0.80}
    ]
  }'
```

#### 8.3.2 获取站点信息

```bash
curl -X GET "http://localhost:8001/api/v1/sites/js01"
```

***

## 9. 常见问题

### 9.1 模型调用失败

**问题描述**：调用AI模型时返回错误

**排查步骤**：

1. 检查 `.env` 文件中的 `DASHSCOPE_API_KEY` 是否正确
2. 检查网络连接是否正常
3. 检查阿里云DashScope服务是否已开通
4. 检查API Key是否有足够的调用额度

**解决方案**：

```bash
# 检查环境变量
cat .env

# 测试网络连接
ping dashscope.aliyuncs.com
```

### 9.2 站点不存在

**问题描述**：调用违规检测接口时返回"站点不存在"

**解决方案**：

1. 确认站点ID是否正确
2. 先调用站点配置接口注册站点
3. 调用获取站点接口确认站点已创建

### 9.3 图片处理失败

**问题描述**：上传图片后处理失败

**排查步骤**：

1. 检查Base64编码是否正确
2. 检查图片格式是否支持（支持JPEG、PNG等常见格式）
3. 检查图片大小是否超过限制（建议小于10MB）

### 9.4 跨域问题

**问题描述**：前端调用API时出现跨域错误

**解决方案**：

1. 确认后端已配置CORS中间件
2. 检查前端API地址配置是否正确
3. 生产环境建议使用Nginx反向代理

### 9.5 图片Base64长度超限

**问题描述**：模型返回 `Range of input length should be [1, 129024]`

**解决方案**：

- 压缩图片尺寸或降低图片质量
- 使用JPEG格式并调整压缩质量

***

## 10. 维护与监控

### 10.1 日志管理

**查看实时日志**：

```bash
# 开发模式
python -m uvicorn main:app --reload --log-level debug

# 生产模式（使用systemd）
journalctl -u vl-marker -f
```

**日志级别配置**：

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### 10.2 数据库备份

**手动备份**：

```bash
# 备份数据库
cp vl_marker.db vl_marker_backup_$(date +%Y%m%d).db
```

**定时备份脚本**：

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/vl-marker"
DATE=$(date +%Y%m%d_%H%M%S)
cp /path/to/vl_marker.db $BACKUP_DIR/vl_marker_$DATE.db

# 保留最近7天的备份
find $BACKUP_DIR -name "vl_marker_*.db" -mtime +7 -delete
```

### 10.3 性能监控

**监控指标**：

- API响应时间
- 模型调用延迟
- 数据库查询性能
- 内存使用情况

**监控工具推荐**：

- Prometheus + Grafana
- ELK Stack（Elasticsearch + Logstash + Kibana）

### 10.4 健康检查

**API健康检查端点**：

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

***

## 11. 项目结构

```
VL-Marker/
├── app/                          # 后端应用目录
│   ├── api/                      # API接口模块
│   │   ├── __init__.py
│   │   ├── sites.py              # 站点配置接口
│   │   └── analyze.py            # 违规检测接口
│   ├── models/                   # 数据模型
│   │   └── db.py                 # 数据库模型定义
│   └── utils/                    # 工具函数
│       ├── db_utils.py           # 数据库操作工具
│       ├── image_utils.py        # 图像处理工具
│       └── model_utils.py        # AI模型调用工具
├── frontend/                     # 前端应用目录
│   ├── src/                      # 源代码目录
│   │   ├── components/           # Vue组件
│   │   ├── views/                # 页面视图
│   │   ├── services/             # API服务
│   │   │   └── api.ts            # API调用封装
│   │   ├── App.vue               # 根组件
│   │   ├── main.ts               # 入口文件
│   │   └── router.ts             # 路由配置
│   ├── public/                   # 静态资源
│   ├── dist/                     # 构建输出目录
│   ├── index.html                # HTML模板
│   ├── package.json              # 项目依赖配置
│   └── vite.config.ts            # Vite配置
├── tests/                        # 测试文件目录
│   ├── test_db.py                # 数据库测试
│   └── test_image.py             # 图像处理测试
├── videos/                       # 视频文件目录（调试用）
├── main.py                       # 应用入口文件
├── requirements.txt              # Python依赖列表
├── .env                          # 环境变量配置
├── vl_marker.db                  # SQLite数据库文件
├── API文档.md                    # API接口文档
└── 部署指南.md                    # 本文档
```

***

## 附录

### A. 依赖版本

```
fastapi
uvicorn[standard]
sqlmodel
opencv-python
pillow
requests
python-dotenv
dashscope
```

### B. 参考链接

- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [Vue 3官方文档](https://vuejs.org/)
- [阿里云DashScope文档](https://help.aliyun.com/zh/dashscope/)
- [OpenCV官方文档](https://docs.opencv.org/)

### C. 更新日志

| 版本    | 日期         | 更新内容   |
| ----- | ---------- | ------ |
| 1.0.0 | 2024-01-01 | 初始版本发布 |

***

如有问题或建议，请联系项目维护人员。
