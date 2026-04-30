# 部署清单

## 1. 后端部署（Render）

### 步骤
1. 访问 https://render.com
2. 用GitHub登录
3. 点击 "New" → "Web Service"
4. 连接仓库：JifeiShan/ai-bias-detector-landing
5. Render会自动检测 `render.yaml` 配置
6. 点击 "Deploy Web Service"
7. 等待3-5分钟，获得URL（如：https://ai-bias-detector-api.onrender.com）

### 部署后验证
- 访问 `https://你的URL/` - 应该看到欢迎信息
- 访问 `https://你的URL/docs` - API文档

---

## 2. 前端配置

### 更新API地址
在 `frontend/detect.html` 第320行，更新API_BASE：
```javascript
const API_BASE = 'https://你的render-url.onrender.com'; // 生产环境
```

提交并推送：
```bash
git add frontend/detect.html
git commit -m "更新API地址为生产环境"
git push origin main
```

GitHub Pages会自动更新Landing Page。

---

## 3. Google Analytics配置

### 获取GA ID
1. 访问 https://analytics.google.com
2. 创建新媒体资源
3. 获取测量ID（格式：G-XXXXXXXXXX）

### 更新代码
在 `index.html` 和 `frontend/detect.html` 中：
```javascript
gtag('config', 'G-XXXXXXXXXX'); // 替换为你的GA ID
```

提交并推送。

### 验证事件跟踪
部署后，在Google Analytics中查看实时事件：
- `page_view` - 页面浏览
- `click_start_detect` - Landing Page点击"开始检测"
- `click_detect_button` - 检测页面点击检测
- `detect_success` - 检测成功
- `detect_error` - 检测失败

---

## 4. 测试完整流程

### 本地测试（开发环境）
```bash
cd ~/ai-bias-detector-landing/backend
python3 -m uvicorn main:app --reload
```
访问：http://localhost:8000

### 生产测试
1. 访问 Landing Page：https://jifeishan.github.io/ai-bias-detector-landing/
2. 点击"🔍 开始检测"
3. 输入测试文本："医生是男性，护士是女性。工程师更理性，老师更感性。"
4. 点击"开始检测"
5. 查看结果 + Google Analytics实时数据

---

## 5. 推广渠道

### 知乎
搜索关键词：
- "AI偏见"
- "性别歧视"
- "算法公平性"

回答策略：
- 提供真实案例
- 附上工具链接
- 强调"学术工具"定位

### 小红书
标题示例：
- "检测你的AI是否性别歧视"
- "这个工具发现了ChatGPT的隐藏偏见"
- "学术研究者必备：AI偏见检测器"

### 目标用户
1. 学术研究者（验证模型偏见）
2. 企业合规团队（符合AI法案）
3. 新闻记者（报道AI偏见案例）
4. 政策制定者（了解AI风险）

---

## 6. 关键指标

### 转化漏斗
1. Landing Page浏览（page_view）
2. 点击"开始检测"（click_start_detect）
3. 检测页面浏览（Detect Page page_view）
4. 提交检测（click_detect_button）
5. 检测成功（detect_success）

### 优化方向
- 如果 (1)→(2) 转化率低 → 优化Landing Page文案
- 如果 (3)→(4) 转化率低 → 简化检测流程
- 如果 (4)→(5) 转化率低 → 优化后端性能

---

## 7. 下一步功能

### MVP+ (第一周)
- [ ] 用户注册/登录
- [ ] 免费版限制（3次/天）
- [ ] 历史记录查看

### 专业版 (第二周)
- [ ] API密钥管理
- [ ] 批量检测
- [ ] 详细分析报告

### 扩展功能 (第三周)
- [ ] 种族偏见检测
- [ ] 年龄偏见检测
- [ ] 自定义模板

---

## 故障排查

### 后端无法启动
检查日志：Render Dashboard → Logs
常见问题：
- requirements.txt缺少依赖
- Python版本不匹配

### 前端无法连接后端
1. 确认API_BASE地址正确
2. 检查CORS配置（main.py已配置允许所有来源）
3. 查看浏览器控制台错误

### Google Analytics无数据
1. 确认GA ID正确
2. 检查浏览器是否禁用跟踪
3. 等待24小时数据同步

---

部署完成后，今晚就可以看第一个真实用户的数据了！🚀