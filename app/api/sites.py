from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
from app.models.db import Site
from app.utils.db_utils import save_site, get_site_by_id

router = APIRouter()

class PolygonPoint(BaseModel):
    x: float = Field(..., ge=0.0, le=1.0, description="相对X坐标，范围0.0-1.0")
    y: float = Field(..., ge=0.0, le=1.0, description="相对Y坐标，范围0.0-1.0")

class SiteConfigRequest(BaseModel):
    site_id: str = Field(..., description="站点唯一标识符")
    site_name: str = Field(..., description="站点业务名称")
    rule_type: str = Field(default="in_bounds", description="规则类型：in_bounds (必须在框内) / no_entry (禁止入内)")
    polygon_cfg: List[PolygonPoint] = Field(..., min_items=3, description="多边形顶点的相对坐标数组，至少3个点")
    reference_image: str = Field(default="", description="参考图片的Base64编码")
    prompt: str = Field(default="请检查视频中是否有车驶入标记的红色区域内，并严格遵守以下json格式进行信息的返回:{\"result\":true/false(用boolean值回答是否有车辆驶入),\"reason\":\"判断理由\"}", description="分析提示词")

class SiteConfigResponse(BaseModel):
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="success", description="响应消息")
    data: dict = Field(..., description="响应数据")

@router.post("/config", response_model=SiteConfigResponse)
async def config_site(request: SiteConfigRequest):
    """注册/更新站点配置"""
    try:
        # 验证规则类型
        if request.rule_type not in ["in_bounds", "no_entry"]:
            raise HTTPException(status_code=400, detail="规则类型无效，只支持in_bounds或no_entry")
        
        # 验证多边形配置
        if len(request.polygon_cfg) < 3:
            raise HTTPException(status_code=400, detail="多边形至少需要3个顶点")
        
        # 转换多边形配置格式
        polygon_cfg = [point.model_dump() for point in request.polygon_cfg]
        
        # 创建或更新站点
        site = Site(
            site_id=request.site_id,
            site_name=request.site_name,
            rule_type=request.rule_type,
            polygon_cfg=polygon_cfg,
            reference_image=request.reference_image,
            prompt=request.prompt
        )
        
        saved_site = save_site(site)
        
        # 构建响应
        response_data = {
            "site_id": saved_site.site_id,
            "site_name": saved_site.site_name,
            "rule_type": saved_site.rule_type,
            "polygon_cfg": saved_site.polygon_cfg,
            "reference_image": saved_site.reference_image,
            "prompt": saved_site.prompt
        }
        
        return SiteConfigResponse(
            code=200,
            message="success",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

@router.get("/{site_id}", response_model=SiteConfigResponse)
async def get_site_info(site_id: str):
    """获取站点配置信息"""
    try:
        # 查询站点
        site = get_site_by_id(site_id)
        if not site:
            raise HTTPException(status_code=404, detail=f"站点 {site_id} 不存在")
        
        # 构建响应
        response_data = {
            "site_id": site.site_id,
            "site_name": site.site_name,
            "rule_type": site.rule_type,
            "polygon_cfg": site.polygon_cfg,
            "reference_image": site.reference_image,
            "prompt": site.prompt
        }
        
        return SiteConfigResponse(
            code=200,
            message="success",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

@router.get("", response_model=SiteConfigResponse)
async def get_all_sites():
    """获取所有站点配置信息"""
    try:
        # 查询所有站点
        from sqlmodel import select
        from app.utils.db_utils import session
        statement = select(Site)
        sites = session.exec(statement).all()
        
        # 构建响应
        response_data = {
            "sites": [{
                "site_id": site.site_id,
                "site_name": site.site_name,
                "rule_type": site.rule_type,
                "polygon_cfg": site.polygon_cfg,
                "reference_image": site.reference_image,
                "prompt": site.prompt,
                "created_at": site.created_at.strftime("%Y-%m-%d %H:%M:%S")
            } for site in sites]
        }
        
        return SiteConfigResponse(
            code=200,
            message="success",
            data=response_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")