import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image

# 创建一个测试图片
img = np.zeros((200, 200, 3), dtype=np.uint8)
cv2.putText(img, 'Test', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# 转换为PIL图像并编码为Base64
pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
buffer = BytesIO()
pil_img.save(buffer, format='JPEG')
base64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

# 保存到文件
with open('test_image_base64.txt', 'w') as f:
    f.write(base64_str)

print("Base64 image saved to test_image_base64.txt")
print(f"First 100 characters: {base64_str[:100]}...")