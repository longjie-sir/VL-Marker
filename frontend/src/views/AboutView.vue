<template>
  <div class="about-container">
    <el-card class="about-card">
      <template #header>
        <div class="card-header">
          <span>关于系统</span>
        </div>
      </template>
      
      <div class="about-content">
        <h2>AI 视觉智能监控系统</h2>
        <p>版本：1.0.0</p>
        <p class="description">
          本系统是一个轻量级、SaaS化、控制面与数据面解耦的AI视觉监控API中台。系统通过接收上游系统抽帧推流的图片，结合用户在前端自定义标注的"空间多边形区域"，利用云端视觉大模型（VLM）强大的图像语义理解能力，实现"零本地算力、高泛化能力"的实时违规行为检测。
        </p>
        <h3>系统架构</h3>
        <ul>
          <li>上游端（客户/设备端）：负责视频流管理、按固定频率抽帧，并将图片转为Base64与站点ID一起发送给本系统。</li>
          <li>配置端（前端控制台）：提供基于Web的可视化界面，用户可上传站点参考底图，使用鼠标绘制监控区域（Polygon），系统保存相对坐标配置。</li>
          <li>AI 中台中枢（本系统核心）：接收推理请求 -> 查询站点坐标配置 -> 使用OpenCV在原图动态绘制区域边界 -> 组装Prompt提交至云端大模型 -> 解析结果并返回给上游。</li>
          <li>模型层：对接阿里云通义千问视觉大模型（Qwen-VL）。</li>
        </ul>
        <h3>技术栈</h3>
        <ul>
          <li>后端：Python 3.10+, FastAPI, SQLite3, SQLModel, OpenCV-Python, 阿里云DashScope SDK</li>
          <li>前端：Vue 3, TypeScript, Element Plus, Fabric.js, Axios</li>
        </ul>
        <h3>核心功能</h3>
        <ul>
          <li>站点管理：支持新建、编辑、删除监控站点</li>
          <li>底图上传：支持上传站点参考底图</li>
          <li>多边形绘制：支持在底图上绘制监控区域</li>
          <li>违规检测：利用云端视觉大模型检测车辆越界等违规行为</li>
        </ul>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
// 关于页面组件
</script>

<style scoped>
.about-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.about-content {
  line-height: 1.6;
}

.description {
  margin: 20px 0;
  text-align: justify;
}

h2 {
  color: #1f2329;
  margin-bottom: 10px;
}

h3 {
  color: #409EFF;
  margin-top: 20px;
  margin-bottom: 10px;
}

ul {
  margin-left: 20px;
  margin-bottom: 20px;
}

li {
  margin-bottom: 5px;
}
</style>