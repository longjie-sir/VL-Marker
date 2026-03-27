<template>
  <div class="sites-container">
    <el-card class="sites-card">
      <template #header>
        <div class="card-header">
          <span>站点管理</span>
          <el-button type="primary" @click="handleAddSite">新建站点</el-button>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 站点管理标签页 -->
        <el-tab-pane label="站点管理" name="sites">
          <el-table :data="sites" style="width: 100%">
            <el-table-column prop="site_id" label="站点ID" width="180" />
            <el-table-column prop="site_name" label="站点名称" />
            <el-table-column prop="rule_type" label="规则类型" width="120">
              <template #default="scope">
                <el-tag :type="scope.row.rule_type === 'in_bounds' ? 'success' : 'danger'">
                  {{ scope.row.rule_type === 'in_bounds' ? '必须在框内' : '禁止入内' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="200" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button type="primary" size="small" @click="handleEditSite(scope.row)">编辑</el-button>
                <el-button type="danger" size="small" @click="handleDeleteSite(scope.row.site_id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <!-- 视频分析标签页 -->
        <el-tab-pane label="视频分析" name="video">
          <el-form label-width="120px">
            <el-form-item label="选择站点">
              <el-select v-model="selectedSiteId" placeholder="请选择站点">
                <el-option
                  v-for="site in sites"
                  :key="site.site_id"
                  :label="site.site_name"
                  :value="site.site_id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="视频上传">
              <el-upload
                class="upload-demo"
                action="#"
                :auto-upload="false"
                :on-change="handleVideoUpload"
                accept=".mp4,.avi,.mov"
                :show-file-list="false"
              >
                <el-button type="primary">选择视频</el-button>
              </el-upload>
              <div v-if="videoFile" style="margin-top: 10px">
                <el-tag size="small">{{ videoFile.name }}</el-tag>
              </div>
            </el-form-item>
            <el-form-item label="抽帧间隔(秒)">
              <el-input-number v-model="frameInterval" :min="0.1" :max="10" :step="0.1" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="processVideo" :disabled="!videoFile || !selectedSiteId">开始处理视频</el-button>
              <el-button type="success" @click="analyzeFrames" :disabled="extractedFrames.length === 0 || !selectedSiteId" style="margin-left: 10px">分析视频帧</el-button>
            </el-form-item>
          </el-form>
          
          <!-- 抽帧结果 -->
          <div v-if="extractedFrames.length > 0" class="frame-results">
            <h3>抽帧结果</h3>
            <div class="frame-grid">
              <div v-for="(frame, index) in extractedFrames" :key="index" class="frame-item">
                <img :src="frame.image" alt="Frame" style="max-width: 200px; max-height: 150px" />
                <div class="frame-info">
                  <span>帧 {{ index + 1 }}</span>
                  <span>时间: {{ frame.time.toFixed(2) }}s</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 分析结果 -->
          <div v-if="analysisResults.length > 0" class="analysis-results">
            <h3>分析结果</h3>
            <el-table :data="analysisResults" style="width: 100%">
              <el-table-column prop="frameIndex" label="帧序号" width="80" />
              <el-table-column prop="time" label="时间(秒)" width="120">
                <template #default="scope">
                  {{ scope.row.time.toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column prop="hasViolation" label="是否违规" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.hasViolation ? 'danger' : 'success'">
                    {{ scope.row.hasViolation ? '是' : '否' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="violationDesc" label="违规描述" />
              <el-table-column prop="latency" label="分析耗时(ms)" width="120" />
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <!-- 站点配置对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="80%"
    >
      <el-form :model="siteForm" label-width="100px">
        <el-form-item label="站点ID">
          <el-input v-model="siteForm.site_id" placeholder="请输入站点ID" />
        </el-form-item>
        <el-form-item label="站点名称">
          <el-input v-model="siteForm.site_name" placeholder="请输入站点名称" />
        </el-form-item>
        <el-form-item label="规则类型">
          <el-radio-group v-model="siteForm.rule_type">
            <el-radio label="in_bounds">必须在框内</el-radio>
            <el-radio label="no_entry">禁止入内</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="分析提示词">
          <el-input
            v-model="siteForm.prompt"
            type="textarea"
            :rows="4"
            placeholder="请输入分析提示词，支持{rule_type}和{polygon}占位符"
          />
          <!-- <el-alert
            title="提示：{rule_type}会被替换为规则类型，{polygon}会被替换为多边形坐标"
            type="info"
            :closable="false"
            show-icon
            style="margin-top: 10px"
          /> -->
        </el-form-item>
        <el-form-item label="底图上传">
          <el-upload
            class="upload-demo"
            action="#"
            :auto-upload="false"
            :on-change="handleImageUpload"
            accept=".jpg,.jpeg,.png"
            :show-file-list="false"
          >
            <el-button type="primary">选择图片</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="多边形绘制">
          <div v-if="siteForm.reference_image" class="canvas-container">
            <canvas ref="canvasRef" :width="canvasWidth" :height="canvasHeight"></canvas>
          </div>
          <div v-else class="canvas-placeholder">
            请先上传底图
          </div>
          <div class="canvas-actions">
            <el-radio-group v-model="drawingMode" size="small">
              <el-radio-button label="draw">绘制</el-radio-button>
              <el-radio-button label="edit">编辑</el-radio-button>
            </el-radio-group>
            <el-button size="small" @click="endDrawing" style="margin-left: 10px" :disabled="drawingMode !== 'draw' || polygonPoints.length < 3">结束绘制</el-button>
            <el-button size="small" @click="clearPolygon" style="margin-left: 10px">清除多边形</el-button>
            <el-button size="small" @click="downloadMergedImage" style="margin-left: 10px" :disabled="polygonPoints.length < 3">下载融合图片</el-button>
            <el-button type="success" size="small" @click="storeImage" style="margin-left: 10px" :disabled="!siteForm.reference_image || polygonPoints.length < 3">入库</el-button>
          </div>
          <div class="canvas-styling" style="margin-top: 10px; display: flex; align-items: center; gap: 20px">
            <div style="display: flex; align-items: center">
              <span style="margin-right: 10px">填充颜色:</span>
              <el-color-picker v-model="fillColor" @change="drawPolygon" />
            </div>
            <div style="display: flex; align-items: center; width: 200px">
              <span style="margin-right: 10px">透明度:</span>
              <el-slider v-model="fillOpacity" @change="drawPolygon" :min="0" :max="1" :step="0.1" />
              <span style="margin-left: 10px">{{ fillOpacity.toFixed(1) }}</span>
            </div>
          </div>
          <div class="canvas-hints">
            <el-alert
              :title="drawingMode === 'draw' ? '绘制模式：点击Canvas添加顶点，右键或点击结束按钮完成绘制' : '编辑模式：拖拽顶点调整多边形形状'"
              type="info"
              :closable="false"
              show-icon
            />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveSite">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { configSite, getSite, analyzeFrame, getAllSites } from '../services/api'

// 站点数据
const sites = ref([
  {
    site_id: 'wh_gate_01',
    site_name: '一号仓库大门',
    rule_type: 'in_bounds',
    created_at: '2026-03-22 10:00:00'
  },
  {
    site_id: 'wh_gate_02',
    site_name: '二号仓库大门',
    rule_type: 'no_entry',
    created_at: '2026-03-22 11:00:00'
  }
])

// 对话框状态
const dialogVisible = ref(false)
const dialogTitle = ref('新建站点')

// 站点表单
const siteForm = ref({
  site_id: '',
  site_name: '',
  rule_type: 'in_bounds',
  reference_image: '',
  polygon_cfg: [] as {x: number, y: number}[],
  prompt: '请检查视频中是否有车驶入标记的红色区域内，并严格遵守以下json格式进行信息的返回:{"result":true/false(用boolean值回答是否有车辆驶入),"reason":"判断理由"}'
})

// 绘制模式
const drawingMode = ref('draw') // 'draw' 或 'edit'

// Canvas相关
const canvasRef = ref<HTMLCanvasElement>()
const canvasWidth = ref(800)
const canvasHeight = ref(600)
let ctx: CanvasRenderingContext2D | null = null
let image: HTMLImageElement | null = null
let polygonPoints = ref<{x: number, y: number}[]>([])
let tempPoint = ref<{x: number, y: number} | null>(null)
let isDragging = false
let draggedPointIndex = -1
let isDrawing = ref(false)
const fillColor = ref('#ff0000')
const fillOpacity = ref(0.3)

// 标签页状态
const activeTab = ref('sites')

// 视频分析相关
const selectedSiteId = ref('')
const videoFile = ref<File | null>(null)
const frameInterval = ref(1.0)
const extractedFrames = ref<{image: string, time: number}[]>([])
const analysisResults = ref<{frameIndex: number, time: number, hasViolation: boolean, violationDesc: string, latency: number}[]>([])

// 初始化Canvas
const initCanvas = () => {
  if (!canvasRef.value) return
  
  const canvas = canvasRef.value
  
  ctx = canvas.getContext('2d')
  if (!ctx) return
  
  // 移除旧的事件监听器，避免重复绑定
  canvas.removeEventListener('mousedown', handleCanvasMouseDown)
  canvas.removeEventListener('mousemove', handleCanvasMouseMove)
  canvas.removeEventListener('mouseup', handleCanvasMouseUp)
  canvas.removeEventListener('dblclick', handleCanvasDoubleClick)
  
  // 绑定事件
  canvas.addEventListener('mousedown', handleCanvasMouseDown)
  canvas.addEventListener('mousemove', handleCanvasMouseMove)
  canvas.addEventListener('mouseup', handleCanvasMouseUp)
  canvas.addEventListener('dblclick', handleCanvasDoubleClick)
  canvas.addEventListener('contextmenu', handleCanvasContextMenu)
  
  // 加载底图
  if (siteForm.value.reference_image) {
    console.log('开始加载图片:', siteForm.value.reference_image.substring(0, 100) + '...')
    
    image = new Image()
    image.onload = () => {
      console.log('图片加载成功:', image?.width, 'x', image?.height)
      if (image && ctx) {
        // 根据图片尺寸调整Canvas大小
        canvas.width = image.width
        canvas.height = image.height
        canvasWidth.value = image.width
        canvasHeight.value = image.height
        
        // 清空画布
        ctx.fillStyle = '#f0f0f0'
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        
        // 绘制图片（完全填充Canvas）
        ctx.drawImage(image, 0, 0, canvas.width, canvas.height)
        
        // 重新计算多边形坐标并绘制
        if (siteForm.value.polygon_cfg && siteForm.value.polygon_cfg.length > 0) {
          // 转换相对坐标为Canvas坐标
          polygonPoints.value = siteForm.value.polygon_cfg.map((point: any) => ({
            x: point.x * canvasWidth.value,
            y: point.y * canvasHeight.value
          }))
        }
        
        // 重新绘制多边形
        drawPolygon()
        
        console.log('图片已添加到Canvas并渲染，Canvas尺寸调整为:', canvas.width, 'x', canvas.height)
      }
    }
    image.onerror = (error) => {
      console.error('图片加载失败:', error)
    }
    image.src = siteForm.value.reference_image
  } else {
    console.log('没有图片需要加载')
    // 没有图片时，设置默认Canvas尺寸
    canvas.width = 800
    canvas.height = 600
    canvasWidth.value = 800
    canvasHeight.value = 600
    
    // 清空画布
    ctx.fillStyle = '#f0f0f0'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
  }
}

// 获取鼠标在Canvas上的坐标（映射到原始图片尺寸）
const getMousePos = (canvas: HTMLCanvasElement, event: MouseEvent) => {
  const rect = canvas.getBoundingClientRect()
  const displayX = event.clientX - rect.left
  const displayY = event.clientY - rect.top
  
  // 计算缩放比例
  const scaleX = canvas.width / rect.width
  const scaleY = canvas.height / rect.height
  
  // 映射到原始图片尺寸
  return {
    x: displayX * scaleX,
    y: displayY * scaleY
  }
}

// 绘制多边形
const drawPolygon = () => {
  if (!ctx || !canvasRef.value) return
  
  const canvas = canvasRef.value
  const width = canvas.width
  const height = canvas.height
  
  // 清空画布
  ctx.fillStyle = '#f0f0f0'
  ctx.fillRect(0, 0, width, height)
  
  // 绘制图片（完全填充Canvas）
  if (image) {
    ctx.drawImage(image, 0, 0, width, height)
  }
  
  // 绘制多边形
  if (polygonPoints.value.length >= 3) {
    ctx.beginPath()
    ctx.moveTo(polygonPoints.value[0].x, polygonPoints.value[0].y)
    for (let i = 1; i < polygonPoints.value.length; i++) {
      ctx.lineTo(polygonPoints.value[i].x, polygonPoints.value[i].y)
    }
    ctx.closePath()
    // 使用自定义颜色和透明度
    const r = parseInt(fillColor.value.substring(1, 3), 16)
    const g = parseInt(fillColor.value.substring(3, 5), 16)
    const b = parseInt(fillColor.value.substring(5, 7), 16)
    ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${fillOpacity.value})`
    ctx.fill()
    ctx.strokeStyle = fillColor.value
    ctx.lineWidth = 2
    ctx.stroke()
  }
  
  // 绘制点标记（仅在绘制过程中显示）
  if (isDrawing.value) {
    polygonPoints.value.forEach((point) => {
      if (ctx) {
        ctx.beginPath()
        ctx.arc(point.x, point.y, 5, 0, Math.PI * 2)
        ctx.fillStyle = 'blue'
        ctx.fill()
        ctx.strokeStyle = 'white'
        ctx.lineWidth = 2
        ctx.stroke()
      }
    })
    
    // 绘制临时线段
    if (polygonPoints.value.length > 0 && tempPoint.value) {
      ctx.beginPath()
      ctx.moveTo(polygonPoints.value[polygonPoints.value.length - 1].x, polygonPoints.value[polygonPoints.value.length - 1].y)
      ctx.lineTo(tempPoint.value.x, tempPoint.value.y)
      ctx.strokeStyle = 'red'
      ctx.lineWidth = 2
      ctx.setLineDash([5, 5])
      ctx.stroke()
      ctx.setLineDash([])
    }
  }
}

// 处理Canvas鼠标按下
const handleCanvasMouseDown = (e: MouseEvent) => {
  if (!canvasRef.value || !ctx) return
  
  const pos = getMousePos(canvasRef.value, e)
  
  if (drawingMode.value === 'draw') {
    // 绘制模式：添加顶点
    polygonPoints.value.push(pos)
    tempPoint.value = null
    isDrawing.value = true
    drawPolygon()
  } else if (drawingMode.value === 'edit') {
    // 编辑模式：检查是否点击了顶点
    const pointRadius = 10
    for (let i = 0; i < polygonPoints.value.length; i++) {
      const point = polygonPoints.value[i]
      const distance = Math.sqrt(Math.pow(pos.x - point.x, 2) + Math.pow(pos.y - point.y, 2))
      if (distance <= pointRadius) {
        isDragging = true
        draggedPointIndex = i
        break
      }
    }
  }
}

// 处理Canvas鼠标移动
const handleCanvasMouseMove = (e: MouseEvent) => {
  if (!canvasRef.value || !ctx) return
  
  const pos = getMousePos(canvasRef.value, e)
  
  if (drawingMode.value === 'draw') {
    // 绘制模式：更新临时线段
    if (polygonPoints.value.length > 0) {
      tempPoint.value = pos
      drawPolygon()
    }
  } else if (drawingMode.value === 'edit' && isDragging && draggedPointIndex >= 0) {
    // 编辑模式：拖动顶点
    polygonPoints.value[draggedPointIndex] = pos
    drawPolygon()
  }
}

// 处理Canvas鼠标释放
const handleCanvasMouseUp = () => {
  isDragging = false
  draggedPointIndex = -1
}

// 处理Canvas双击完成绘制
const handleCanvasDoubleClick = () => {
  // 双击完成绘制，这里可以添加完成绘制的逻辑
  endDrawing()
}

// 处理Canvas右键点击
const handleCanvasContextMenu = (e: MouseEvent) => {
  e.preventDefault() // 阻止默认右键菜单
  if (drawingMode.value === 'draw' && polygonPoints.value.length >= 3) {
    endDrawing()
  }
}

// 结束绘制
const endDrawing = () => {
  if (polygonPoints.value.length >= 3) {
    tempPoint.value = null
    isDrawing.value = false
    drawPolygon()
    ElMessage.success('绘制完成')
  }
}

// 清除多边形
const clearPolygon = () => {
  polygonPoints.value = []
  tempPoint.value = null
  isDrawing.value = false
  drawPolygon()
}

// 处理图片上传
const handleImageUpload = (file: any) => {
  console.log('开始上传图片:', file.name)
  const reader = new FileReader()
  reader.onload = (e) => {
    console.log('图片读取完成')
    siteForm.value.reference_image = e.target?.result as string
    console.log('siteForm.reference_image已设置:', siteForm.value.reference_image ? '是' : '否')
    nextTick(() => {
      console.log('调用initCanvas')
      initCanvas()
      // 显示图片上传成功的提示
      ElMessage.success('图片上传成功')
    })
  }
  reader.onerror = (e) => {
    console.error('图片读取失败:', e)
    ElMessage.error('图片读取失败')
  }
  reader.readAsDataURL(file.raw)
}

// 处理视频上传
const handleVideoUpload = (file: any) => {
  console.log('开始上传视频:', file.name)
  videoFile.value = file.raw
  ElMessage.success('视频上传成功')
}

// 处理视频抽帧
const processVideo = () => {
  if (!videoFile.value) {
    ElMessage.error('请先选择视频文件')
    return
  }
  
  if (!selectedSiteId.value) {
    ElMessage.error('请先选择站点')
    return
  }
  
  ElMessage.info('开始处理视频，请稍候...')
  
  // 使用HTML5 Video和Canvas进行视频抽帧
  const video = document.createElement('video')
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  
  if (!ctx) {
    ElMessage.error('Canvas初始化失败')
    return
  }
  
  video.src = URL.createObjectURL(videoFile.value)
  video.onloadedmetadata = () => {
    console.log('视频元数据加载完成:', {
      duration: video.duration,
      width: video.videoWidth,
      height: video.videoHeight
    })
    
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    // 开始抽帧
    extractedFrames.value = []
    let currentTime = 0
    const interval = frameInterval.value
    
    const extractFrame = () => {
      if (currentTime >= video.duration) {
        ElMessage.success(`视频处理完成，共提取 ${extractedFrames.value.length} 帧`) 
        return
      }
      
      video.currentTime = currentTime
    }
    
    video.onseeked = () => {
      // 绘制当前帧到Canvas
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
      
      // 将Canvas转换为Base64
      const imageData = canvas.toDataURL('image/png')
      extractedFrames.value.push({
        image: imageData,
        time: currentTime
      })
      
      // 处理下一帧
      currentTime += interval
      if (currentTime < video.duration) {
        setTimeout(extractFrame, 100)
      } else {
        ElMessage.success(`视频处理完成，共提取 ${extractedFrames.value.length} 帧`) 
      }
    }
    
    // 开始抽帧
    extractFrame()
  }
  
  video.onerror = (error) => {
    console.error('视频加载失败:', error)
    ElMessage.error('视频加载失败')
  }
}

// 分析视频帧
const analyzeFrames = async () => {
  if (extractedFrames.value.length === 0) {
    ElMessage.error('请先处理视频并提取帧')
    return
  }
  
  if (!selectedSiteId.value) {
    ElMessage.error('请先选择站点')
    return
  }
  
  ElMessage.info('开始分析视频帧，请稍候...')
  
  analysisResults.value = []
  let processedCount = 0
  
  for (let i = 0; i < extractedFrames.value.length; i++) {
    const frame = extractedFrames.value[i]
    
    try {
      // 调用后端API分析帧
      const response = await analyzeFrame(selectedSiteId.value, frame.image)
      console.log(`分析帧 ${i + 1} API响应:`, response)
      
      // 添加到分析结果
      analysisResults.value.push({
        frameIndex: i + 1,
        time: frame.time,
        hasViolation: response.data.has_violation,
        violationDesc: response.data.violation_desc,
        latency: response.data.model_latency_ms
      })
    } catch (error) {
      console.error(`分析帧 ${i + 1} 失败:`, error)
      // 添加错误结果
      analysisResults.value.push({
        frameIndex: i + 1,
        time: frame.time,
        hasViolation: false,
        violationDesc: '分析失败',
        latency: 0
      })
    }
    
    processedCount++
    if (processedCount === extractedFrames.value.length) {
      ElMessage.success(`视频帧分析完成，共分析 ${processedCount} 帧`)
    }
  }
}

// 新建站点
const handleAddSite = () => {
  dialogTitle.value = '新建站点'
  siteForm.value = {
    site_id: '',
    site_name: '',
    rule_type: 'in_bounds',
    reference_image: '',
    polygon_cfg: []
  }
  polygonPoints.value = []
  tempPoint.value = null
  dialogVisible.value = true
  nextTick(() => {
    initCanvas()
  })
}

// 编辑站点
const handleEditSite = async (site: any) => {
  dialogTitle.value = '编辑站点'
  
  try {
    // 调用后端API获取站点详情
    const response = await getSite(site.site_id)
    console.log('获取站点API响应:', response)
    
    // 更新站点表单数据
    siteForm.value = {
      ...site,
      polygon_cfg: response.data.polygon_cfg || [],
      reference_image: response.data.reference_image || '',
      prompt: response.data.prompt || '请分析图片中是否有人员或物体违反规则。规则类型：{rule_type}。多边形区域：{polygon}'
    }
    
    tempPoint.value = null
    dialogVisible.value = true
    
    nextTick(() => {
      initCanvas()
      // 等待图片加载完成后转换坐标
      setTimeout(() => {
        // 转换相对坐标为Canvas坐标
        polygonPoints.value = (response.data.polygon_cfg || []).map((point: any) => ({
          x: point.x * canvasWidth.value,
          y: point.y * canvasHeight.value
        }))
        // 重新绘制多边形
        drawPolygon()
      }, 100)
    })
  } catch (error) {
    console.error('获取站点信息失败:', error)
    // 处理API 404错误，使用本地数据
    ElMessage.info('使用本地站点数据进行编辑')
    
    // 使用本地站点数据
    siteForm.value = { 
      ...site,
      reference_image: site.reference_image || '',
      prompt: site.prompt || '请分析图片中是否有人员或物体违反规则。规则类型：{rule_type}。多边形区域：{polygon}'
    }
    // 确保polygon_cfg存在
    if (!siteForm.value.polygon_cfg) {
      siteForm.value.polygon_cfg = []
    }
    
    tempPoint.value = null
    dialogVisible.value = true
    
    nextTick(() => {
      initCanvas()
      // 等待图片加载完成后转换坐标
      setTimeout(() => {
        // 转换相对坐标为Canvas坐标
        polygonPoints.value = siteForm.value.polygon_cfg.map((point: any) => ({
          x: point.x * canvasWidth.value,
          y: point.y * canvasHeight.value
        }))
        // 重新绘制多边形
        drawPolygon()
      }, 100)
    })
  }
}

// 删除站点
const handleDeleteSite = (siteId: string) => {
  ElMessageBox.confirm('确定要删除该站点吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    sites.value = sites.value.filter(site => site.site_id !== siteId)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

// 下载融合后的图片
const downloadMergedImage = () => {
  if (!canvasRef.value) return
  
  // 确保所有元素都已渲染
  drawPolygon()
  
  try {
    // 创建下载链接
    const link = document.createElement('a')
    link.download = `merged_${Date.now()}.png`
    link.href = canvasRef.value.toDataURL('image/png')
    link.click()
    
    ElMessage.success('图片下载成功')
  } catch (error) {
    console.error('下载图片失败:', error)
    ElMessage.error('下载图片失败，请重试')
  }
}

// 入库图片
const storeImage = async () => {
  if (!canvasRef.value) return
  
  // 确保所有元素都已渲染
  drawPolygon()
  
  try {
    // 生成融合后的图片
    const mergedImage = canvasRef.value.toDataURL('image/png')
    
    // 转换坐标为相对坐标
    const relativePoints = polygonPoints.value.map(point => ({
      x: parseFloat((point.x / canvasWidth.value).toFixed(4)),
      y: parseFloat((point.y / canvasHeight.value).toFixed(4))
    }))
    
    // 更新站点表单数据
    siteForm.value.reference_image = mergedImage
    siteForm.value.polygon_cfg = relativePoints
    
    // 检查是否是新增还是编辑
    const existingIndex = sites.value.findIndex(site => site.site_id === siteForm.value.site_id)
    if (existingIndex >= 0) {
      // 编辑：询问用户是否替换现有图片
      ElMessageBox.confirm('确定要替换现有站点图片吗？', '确认替换', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          // 调用后端API更新站点
          const response = await configSite(siteForm.value)
          console.log('更新站点API响应:', response)
          
          // 更新本地站点数据
          sites.value[existingIndex] = { ...siteForm.value, created_at: new Date().toLocaleString() }
          ElMessage.success('站点图片更新成功')
        } catch (error) {
          console.error('更新站点失败:', error)
          ElMessage.error('更新失败，请重试')
        }
      }).catch(() => {
        // 用户取消替换
      })
    } else {
      // 新增：提示用户需要先填写站点信息并保存
      ElMessage.warning('请先填写站点信息并点击保存按钮')
    }
  } catch (error) {
    console.error('入库失败:', error)
    ElMessage.error('入库失败，请重试')
  }
}

// 保存站点
const handleSaveSite = async () => {
  // 验证表单
  if (!siteForm.value.site_id) {
    ElMessage.error('请输入站点ID')
    return
  }
  if (!siteForm.value.site_name) {
    ElMessage.error('请输入站点名称')
    return
  }
  if (!siteForm.value.reference_image) {
    ElMessage.error('请上传底图')
    return
  }
  if (polygonPoints.value.length < 3) {
    ElMessage.error('请绘制完整的多边形区域')
    return
  }
  
  // 转换坐标为相对坐标
  const relativePoints = polygonPoints.value.map(point => ({
    x: parseFloat((point.x / canvasWidth.value).toFixed(4)),
    y: parseFloat((point.y / canvasHeight.value).toFixed(4))
  }))
  
  siteForm.value.polygon_cfg = relativePoints
  
  try {
    // 调用后端API
    const response = await configSite(siteForm.value)
    console.log('保存站点API响应:', response)
    
    // 检查是否是新增还是编辑
    const existingIndex = sites.value.findIndex(site => site.site_id === siteForm.value.site_id)
    if (existingIndex >= 0) {
      // 编辑
      sites.value[existingIndex] = { ...siteForm.value, created_at: new Date().toLocaleString() }
    } else {
      // 新增
      sites.value.push({ ...siteForm.value, created_at: new Date().toLocaleString() })
    }
    
    ElMessage.success('保存成功')
    dialogVisible.value = false
  } catch (error) {
    console.error('保存站点失败:', error)
    ElMessage.error('保存失败，请重试')
  }
}

// 加载所有站点
const loadSites = async () => {
  try {
    // 调用后端API获取所有站点
    const response = await getAllSites()
    console.log('获取所有站点API响应:', response)
    
    if (response && response.data && response.data.sites) {
      sites.value = response.data.sites
      console.log('站点数据加载成功:', sites.value.length, '个站点')
    }
  } catch (error) {
    console.error('加载站点失败:', error)
  }
}

// 组件挂载后初始化
onMounted(() => {
  nextTick(() => {
    initCanvas()
    loadSites()
  })
})
</script>

<style scoped>
.sites-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.canvas-container {
  border: 1px solid #dcdfe6;
  margin: 10px 0;
  position: relative;
  overflow: hidden;
}

.canvas-container canvas {
  display: block;
  cursor: crosshair;
  max-width: 800px;
  max-height: 600px;
  width: auto;
  height: auto;
}

.canvas-placeholder {
  border: 1px solid #dcdfe6;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  margin: 10px 0;
}

.canvas-actions {
  margin-top: 10px;
}

.canvas-hints {
  margin-top: 10px;
}

.image-preview {
  margin-top: 10px;
}

.dialog-footer {
  text-align: right;
}

.frame-results {
  margin-top: 20px;
}

.frame-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 10px;
}

.frame-item {
  border: 1px solid #dcdfe6;
  padding: 10px;
  border-radius: 4px;
  text-align: center;
  width: 220px;
}

.frame-info {
  margin-top: 10px;
  font-size: 12px;
  color: #606266;
}

.frame-info span {
  display: block;
  margin-bottom: 5px;
}
</style>