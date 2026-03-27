from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import sites, analyze

app = FastAPI(
    title="AI 视觉智能监控 API 中台系统",
    description="一个轻量级、SaaS化、控制面与数据面解耦的AI视觉监控API中台系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

app.include_router(sites.router, prefix="/api/v1/sites", tags=["sites"])
app.include_router(analyze.router, prefix="/api/v1/analyze", tags=["analyze"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)