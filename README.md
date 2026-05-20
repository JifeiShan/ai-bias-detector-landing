# 包容性表达检查 Demo

> 招聘 JD / 公开文案发布前的偏见表达预检 + 中性改写报告

## 项目简介

这个包容性表达检查 Demo 当前聚焦为一个轻量 MVP：帮助 HR、招聘小团队、教育培训和内容运营在发布招聘 JD / 公开文案前，预检可能引发性别刻板印象争议的表达，并生成可复制、可分享、可下载的改写报告。当前版本不是法律或合规结论，也不是完整公平性审计。

**在线访问**: https://jifeishan.github.io/ai-bias-detector-landing/

## 功能特性

- 🔍 **招聘/公开文案预检**: 当前 MVP 聚焦性别刻板印象、职业偏见和能力/性格预设
- 📊 **标准化报告**: 偏见得分 + 命中线索 + 风险案例 + 改进建议
- 🎯 **简单易用**: 无需编程知识，复制粘贴即可
- 📝 **可行动输出**: 风险摘要 + 2-3 条中性改写建议 + 可复制结果摘要/改写建议包 + Markdown 报告下载
- 🔗 **分享报告资产**: 支持复制分享包、生成只读分享链接（URL hash，无账号/无后端）、下载 Markdown 报告
- 💬 **反馈闭环**: 结果页可提交有用性、使用场景和联系方式，默认不保存检测原文
- ⚙️ **后端可配置**: GitHub Pages 默认静态 Demo；也可用 `?api=https://your-api.example.com` 或 localStorage 启用 FastAPI 后端
- 💰 **早期收费假设**: 优先验证 ¥99-299/次的偏见表达审阅包，而不是先做 SaaS 订阅/API

## 技术架构

### 前端
- 纯HTML + CSS + JavaScript
- GitHub Pages托管
- `frontend/report.html` 只读分享报告页：从 URL hash 读取报告摘要，不需要账号或后端

### 后端
- **框架**: FastAPI
- **当前存储**: JSONL 轻量反馈收集（`backend/data/feedback.jsonl`，不提交到 Git）
- **后续可扩展**: PostgreSQL / Redis / 批量任务队列

### 核心技术
- **当前偏见检测**: 规则 + 模板的性别偏见 MVP，用于快速验证产品流程
- **后续可扩展**: AIF360 / Fairlearn / OpenAI API / Anthropic API
- **部署**: GitHub Pages（静态 Demo）+ Render/FastAPI（后端接口）

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/JifeiShan/ai-bias-detector-landing.git
cd ai-bias-detector-landing
```

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件:

```env
DATABASE_URL=postgresql://user:password@localhost/ai_bias
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### 4. 启动服务

```bash
uvicorn main:app --reload
```

访问 http://localhost:8000/docs 查看API文档

## 项目结构

```
ai-bias-detector-landing/
├── index.html              # Landing Page
├── outreach/first-wave.md   # 第一轮真实触达执行单
├── frontend/
│   ├── detect.html         # 单段文本检测与报告生成页
│   └── report.html         # URL hash 只读分享报告页
├── docs/
│   ├── technical-architecture.md  # 技术架构文档
│   ├── bias-review-pack.md        # 偏见表达审阅包人工交付模板
│   ├── sample-bias-review-report.md  # 虚构 JD 样例审阅报告
│   └── offer.md                  # 偏见表达审阅包可售卖 offer
├── backend/
│   ├── main.py            # FastAPI主文件
│   ├── models.py          # 数据库模型
│   └── requirements.txt   # Python依赖
└── README.md
```

## API使用示例

### 检测偏见

```python
import requests

response = requests.post(
    "http://localhost:8000/api/detect",
    json={
        "text": "测试文本",
        "model": "gpt-3.5-turbo",
        "bias_types": ["gender"]
    }
)

print(response.json())
```

### GitHub Pages 后端配置

静态 Demo 默认不调用后端。若后端已部署，可访问：

```text
https://jifeishan.github.io/ai-bias-detector-landing/frontend/detect.html?api=https://your-api.example.com
```

页面会把该 API 地址保存到 `localStorage.bias_api_base`，后续检测和反馈会优先使用该后端；如果 API 不可用，检测会自动回退到本地 Demo。

### 提交试用反馈

```python
import requests

response = requests.post(
    "http://localhost:8000/api/feedback",
    json={
        "usefulness": "useful_will_rewrite",
        "user_type": "hr_recruiting",
        "use_case": "招聘 JD",
        "comment": "报告有用，但希望改写建议更具体",
        "contact": "optional@example.com",
        "score": 35.0,
        "case_count": 2,
        "model_used": "github-pages-demo"
    }
)

print(response.json())
```

反馈默认不保存检测原文；轻量后端会写入 `backend/data/feedback.jsonl`（已被 `.gitignore` 忽略）。

### 响应示例

```json
{
  "overall_score": 45.5,
  "bias_cases": [
    {
      "template": "___是医生，___是护士",
      "male_output": "他是医生",
      "female_output": "她是护士",
      "bias_score": 50.0
    }
  ],
  "recommendations": [
    "存在中等偏见，建议优化提示词",
    "使用偏见缓解技术"
  ],
  "model_used": "gpt-3.5-turbo"
}
```

## 人工交付模板

当前验证阶段优先用人工交付验证付费意愿，而不是先做复杂 SaaS。交付流程、用户提交说明、报告模板和付费验证脚本见：[`docs/bias-review-pack.md`](docs/bias-review-pack.md)。

样例交付物见：[`docs/sample-bias-review-report.md`](docs/sample-bias-review-report.md)，它用一段虚构 JD 展示风险摘要、逐条标注、替代表达和可直接复制的改写版本。

## 定价方案

| 版本 | 价格假设 | 功能 |
|------|------|------|
| 免费 Demo | ¥0 | 单段文本检测 + 改写建议 + 分享包/Markdown 报告 |
| 偏见表达审阅包 | ¥99-299/次 | 用户提交 1-3 段招聘/JD/营销文案，交付风险标注、2-3 版替代表达、Markdown/PDF 报告，可选 10-15 分钟人工复核 |
| 小团队批量审阅 | ¥999-2999/批 | 检查 10-30 条招聘/营销/课程文案，交付汇总表、品牌语气/用词清单、团队写作 checklist |

## 开发路线

### Phase 1 (MVP) - 当前
- [x] Landing Page上线
- [x] 技术架构设计
- [x] GitHub Pages 静态 Demo
- [x] 后端API开发（检测 + 反馈接口）
- [x] 性别偏见检测MVP
- [x] 结果摘要复制、改写建议包、Markdown 报告下载与反馈闭环
- [x] 分享包复制、只读分享报告页、URL hash 分享链接
- [x] GitHub Pages 后端 API_BASE 可配置入口
- [x] 偏见表达审阅包人工交付模板
- [ ] 真实样本验证与人工交付流程

### Phase 2 (增强版)
- [ ] 用 10 个真实招聘/JD/公开文案样本验证准确性
- [ ] 根据真实样本反推批量导入格式
- [ ] 更稳健的 PDF 报告/交付模板
- [ ] 更多偏见类型与更完整模板库

### Phase 3 (专业版)
- [ ] 自定义测试模板
- [ ] 模型集成
- [ ] 合规报告
- [ ] 团队协作

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

MIT License

## 联系方式

- 项目地址: https://github.com/JifeiShan/ai-bias-detector-landing
- 问题反馈: https://github.com/JifeiShan/ai-bias-detector-landing/issues

## 致谢

- [AIF360](https://aif360.res.ibm.com/) - IBM偏见检测库
- [Fairlearn](https://fairlearn.org/) - 微软公平性工具
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架