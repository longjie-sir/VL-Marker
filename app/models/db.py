from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON

class Site(SQLModel, table=True):
    site_id: str = Field(primary_key=True, description="站点唯一标识符")
    site_name: str = Field(..., description="站点业务名称")
    polygon_cfg: list = Field(sa_column=Column(JSON), description="多边形顶点的相对坐标数组")
    rule_type: str = Field(default="in_bounds", description="规则类型：in_bounds (必须在框内) / no_entry (禁止入内)")
    reference_image: str = Field(default="", description="参考图片的Base64编码")
    prompt: str = Field(default="请检查视频中是否有车驶入标记的红色区域内，并严格遵守以下json格式进行信息的返回:{\"result\":true/false(用boolean值回答是否有车辆驶入),\"reason\":\"判断理由\"}", description="分析提示词")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

# 数据库初始化函数
def init_db():
    from sqlmodel import create_engine, Session
    engine = create_engine("sqlite:///./vl_marker.db")
    SQLModel.metadata.create_all(engine)
    return engine, Session(engine)