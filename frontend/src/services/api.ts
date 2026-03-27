// API服务

const API_BASE_URL = 'http://localhost:8001/api/v1';

// 站点配置接口
export const configSite = async (siteData: any) => {
  try {
    const response = await fetch(`${API_BASE_URL}/sites/config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        site_id: siteData.site_id,
        site_name: siteData.site_name,
        rule_type: siteData.rule_type,
        polygon_cfg: siteData.polygon_cfg,
        reference_image: siteData.reference_image,
        prompt: siteData.prompt
      })
    });
    
    if (!response.ok) {
      throw new Error(`API调用失败: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('站点配置API调用失败:', error);
    throw error;
  }
};

// 获取站点信息接口
export const getSite = async (siteId: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/sites/${siteId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`API调用失败: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('获取站点信息API调用失败:', error);
    throw error;
  }
};

// 分析图片接口
export const analyzeFrame = async (siteId: string, imageBase64: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze/frame`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        site_id: siteId,
        image_base64: imageBase64
      })
    });
    
    if (!response.ok) {
      throw new Error(`API调用失败: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('分析图片API调用失败:', error);
    throw error;
  }
};

// 获取所有站点接口
export const getAllSites = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/sites`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`API调用失败: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('获取所有站点API调用失败:', error);
    throw error;
  }
};
