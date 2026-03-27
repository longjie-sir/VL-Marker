from app.models.db import init_db, Site

# 初始化数据库
engine, session = init_db()

# 添加测试站点
test_site = Site(
    site_id="test_site_001",
    site_name="测试站点",
    polygon_cfg=[
        {"x": 0.2, "y": 0.2},
        {"x": 0.8, "y": 0.2},
        {"x": 0.8, "y": 0.8},
        {"x": 0.2, "y": 0.8}
    ],
    rule_type="in_bounds"
)

session.add(test_site)
session.commit()
session.close()

print("数据库初始化完成，添加了测试站点 test_site_001")
