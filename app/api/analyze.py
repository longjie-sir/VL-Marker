from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.utils.db_utils import get_site_by_id
from app.utils.image_utils import process_image, decode_base64_image, save_image_to_file
from app.utils.model_utils import call_qwen_vl
import os
from datetime import datetime

router = APIRouter()

class AnalyzeFrameRequest(BaseModel):
    site_id: str = Field(..., description="站点唯一标识符")
    image_base64: str = Field(..., description="Base64编码的图片")

class AnalyzeFrameResponse(BaseModel):
    code: int = Field(default=200, description="响应状态码")
    message: str = Field(default="success", description="响应消息")
    data: dict = Field(..., description="响应数据")

@router.post("/frame", response_model=AnalyzeFrameResponse)
async def analyze_frame(request: AnalyzeFrameRequest):
    """执行单帧图片违规检测"""
    try:
        # 1. 查询站点配置
        site = get_site_by_id(request.site_id)
        if not site:
            raise HTTPException(status_code=404, detail=f"站点 {request.site_id} 不存在")
        
        # 2. 处理图片（解码、绘制多边形）
        processed_image = process_image(request.image_base64, site.polygon_cfg)
        
        # [调试功能] 保存融合后的图片到本地，部署后可注释掉以下代码块
        try:
            # 解码融合后的图片
            image_with_polygon = decode_base64_image(processed_image)
            # 生成时间戳文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            save_path = os.path.join("d:\\Projects\\Python\\VL-Marker\\videos", f"fused_frame_{timestamp}.jpg")
            # 保存图片
            save_image_to_file(image_with_polygon, save_path)
            #print(f"[调试] 融合图片已保存到: {save_path}")
        except Exception as save_error:
            print(f"[调试] 保存融合图片失败: {str(save_error)}")
        # [调试功能结束]
        
        # 3. 调用模型进行违规检测
        # 替换prompt中的占位符
        prompt = site.prompt
       # prompt = prompt.replace('{rule_type}', '必须在框内' if site.rule_type == 'in_bounds' else '禁止入内')
        #prompt = prompt.replace('{polygon}', str(site.polygon_cfg))       
        model_result = call_qwen_vl(processed_image, prompt)

        # 4. 构建响应
        response_data = {
            "site_id": request.site_id,
            "has_violation": model_result["has_violation"],
            "violation_desc": model_result["violation_desc"],
            "model_latency_ms": model_result["model_latency_ms"]
        }
        
        return AnalyzeFrameResponse(
            code=200,
            message="success",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")