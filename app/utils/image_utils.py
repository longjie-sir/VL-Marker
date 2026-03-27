import cv2
import numpy as np
import base64
from PIL import Image
from io import BytesIO
from typing import List, Dict

def decode_base64_image(base64_str: str) -> np.ndarray:
    """解码Base64编码的图片为OpenCV图像矩阵"""
    # 移除Base64前缀（如果有）
    if base64_str.startswith('data:image'):
        base64_str = base64_str.split(',')[1]
    
    # 解码Base64字符串
    image_data = base64.b64decode(base64_str)
    
    # 将字节数据转换为PIL图像
    pil_image = Image.open(BytesIO(image_data))
    
    # 转换为OpenCV格式（BGR）
    cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    return cv_image

def encode_image_to_base64(image: np.ndarray) -> str:
    """将OpenCV图像矩阵编码为Base64字符串"""
    # 转换为RGB格式
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 创建PIL图像
    pil_image = Image.fromarray(rgb_image)
    
    # 保存到BytesIO
    buffer = BytesIO()
    pil_image.save(buffer, format='JPEG')
    
    # 编码为Base64
    base64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return base64_str

def draw_polygon(image: np.ndarray, polygon_cfg: List[Dict[str, float]]) -> np.ndarray:
    """在图片上绘制透明度为0.3的红色填充多边形区域"""
    # 获取图片尺寸
    height, width = image.shape[:2]
    
    # 转换相对坐标为绝对像素
    points = []
    for point in polygon_cfg:
        x = int(point['x'] * width)
        y = int(point['y'] * height)
        points.append([x, y])
    
    # 转换为numpy数组
    points = np.array(points, dtype=np.int32)
    
    # 创建overlay层
    overlay = image.copy()
    
    # 绘制填充多边形（红色，BGR格式）
    cv2.fillPoly(overlay, [points], color=(0, 0, 255))
    
    # 将overlay与原图融合，透明度为0.3
    alpha = 0.3
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
    
    return image

def save_image_to_file(image: np.ndarray, file_path: str) -> str:
    """
    将OpenCV图像矩阵保存为文件
    
    Args:
        image: OpenCV图像矩阵 (BGR格式)
        file_path: 保存路径
    
    Returns:
        保存的文件路径
    """
    # 转换为RGB格式
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 创建PIL图像
    pil_image = Image.fromarray(rgb_image)
    
    # 保存到文件
    pil_image.save(file_path, format='JPEG', quality=95)
    
    return file_path

def process_image(base64_str: str, polygon_cfg: List[Dict[str, float]]) -> str:
    """处理图片：解码 -> 绘制多边形 -> 编码"""
    # 解码图片
    image = decode_base64_image(base64_str)
    
    # 绘制多边形
    image_with_polygon = draw_polygon(image, polygon_cfg)
    
    # 编码为Base64
    processed_base64 = encode_image_to_base64(image_with_polygon)
    
    return processed_base64