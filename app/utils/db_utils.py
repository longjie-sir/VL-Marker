from app.models.db import Site, init_db
from sqlmodel import Session

# 初始化数据库引擎和会话
engine, session = init_db()

def get_site_by_id(site_id: str) -> Site:
    """根据站点ID获取站点配置"""
    return session.get(Site, site_id)

def save_site(site: Site) -> Site:
    """保存站点配置（创建或更新）"""
    existing_site = get_site_by_id(site.site_id)
    if existing_site:
        # 更新现有站点
        existing_site.site_name = site.site_name
        existing_site.polygon_cfg = site.polygon_cfg
        existing_site.rule_type = site.rule_type
        existing_site.reference_image = site.reference_image
        existing_site.prompt = site.prompt
        session.add(existing_site)
        session.commit()
        session.refresh(existing_site)
        return existing_site
    else:
        # 创建新站点
        session.add(site)
        session.commit()
        session.refresh(site)
        return site

def close_db():
    """关闭数据库会话"""
    session.close()