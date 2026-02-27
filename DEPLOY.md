# 快速部署指南

## 1. 安装依赖

```bash
cd /root/.openclaw/workspace/corp-finance-analyzer

# 使用 pip 安装
pip install -r requirements.txt
```

## 2. 配置 API Key

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，填入你的通义千问 API Key
# 获取地址：https://dashscope.console.aliyun.com/apiKey
```

## 3. 运行应用

```bash
# 方式一：使用运行脚本
./run.sh

# 方式二：直接运行
python3 app.py
```

## 4. 访问应用

打开浏览器访问：http://localhost:5000

## 5. 功能说明

### 上传年报
- 支持 PDF 格式
- 最大 50MB
- 拖拽或点击上传

### 自动分析
- 📈 财务指标提取（营收、利润、资产等）
- 📝 MD&A 文本分析
- 🤖 AI 智能洞察（盈利能力、发展前景、投资价值）
- 📊 可视化图表

### 教学用途
- 公司金融课程演示
- 财务报表分析教学
- AI 在金融中的应用案例

## 常见问题

### Q: API Key 在哪里获取？
A: 访问 https://dashscope.console.aliyun.com/apiKey 注册阿里云账号并获取

### Q: 支持哪些年报格式？
A: 目前支持 PDF 格式的上市公司年报

### Q: 分析准确度如何？
A: 财务指标通过正则提取，准确率取决于年报格式；AI 分析基于通义千问大模型

### Q: 可以自定义分析维度吗？
A: 可以修改 analyzer.py 中的 prompt 来调整分析维度

## 技术架构

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   前端界面   │────▶│  Flask 后端  │────▶│  分析引擎   │
│ TailwindCSS │     │   REST API   │     │  大模型 API  │
│  Chart.js   │     │  文件处理    │     │  财务分析   │
└─────────────┘     └──────────────┘     └─────────────┘
```

## 扩展建议

1. **添加更多数据源**：支持 Excel、CSV 格式
2. **历史对比**：多年财报数据对比分析
3. **同行对比**：同行业公司指标对比
4. **导出报告**：生成 PDF 分析报告
5. **用户系统**：保存分析历史记录

---

**Happy Analyzing! 📊**
