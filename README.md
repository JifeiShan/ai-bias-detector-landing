# AI偏见检测工具

> 发现隐藏的偏见，构建更公平的AI

## 项目简介

AI偏见检测工具帮助用户自动检测AI输出中的性别、种族、年龄、职业偏见，生成标准化报告，适用于学术研究、企业合规、新闻媒体等场景。

**在线访问**: https://jifeishan.github.io/ai-bias-detector-landing/

## 功能特性

- 🔍 **多类型偏见检测**: 性别、种族、年龄、职业
- 📊 **标准化报告**: 偏见得分 + 具体案例 + 改进建议
- 🎯 **简单易用**: 无需编程知识，复制粘贴即可
- 📝 **可行动输出**: 风险摘要 + 命中线索 + 中性改写建议 + 可复制结果摘要
- 💬 **反馈闭环**: 结果页可提交有用性、使用场景和联系方式，默认不保存检测原文
- 📈 **API接口**: 支持开发者集成
- 💰 **灵活定价**: 免费/专业/团队版本

## 技术架构

### 前端
- 纯HTML + CSS + JavaScript
- GitHub Pages托管

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
├── docs/
│   └── technical-architecture.md  # 技术架构文档
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

## 定价方案

| 版本 | 价格 | 功能 |
|------|------|------|
| 免费版 | ¥0/月 | 每天3次检测 + 基础报告 |
| 专业版 | ¥99/月 | 无限检测 + 详细分析 + API |
| 团队版 | ¥999/月 | 多用户 + 批量检测 + 自定义 |

## 开发路线

### Phase 1 (MVP) - 当前
- [x] Landing Page上线
- [x] 技术架构设计
- [x] GitHub Pages 静态 Demo
- [x] 后端API开发（检测 + 反馈接口）
- [x] 性别偏见检测MVP
- [x] 结果摘要复制与反馈闭环
- [ ] 用户系统

### Phase 2 (增强版)
- [ ] API接口完善
- [ ] 批量检测功能
- [ ] 更多偏见类型
- [ ] 详细分析报告

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