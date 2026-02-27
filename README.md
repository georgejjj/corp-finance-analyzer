# 公司金融年报分析系统

基于大模型的公司年报自动化分析教学演示系统

## 功能特性

- 📤 PDF 年报上传
- 📈 财务指标量化分析
- 📝 管理层讨论与分析 (MD&A) 文本分析
- 🤖 大模型智能洞察
- 📊 可视化图表展示

## 技术栈

- **前端**: HTML5 + TailwindCSS + Chart.js
- **后端**: Python + Flask
- **PDF 处理**: PyMuPDF (fitz)
- **大模型**: 通义千问 API

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 设置 API Key
export DASHSCOPE_API_KEY="your-api-key"

# 运行应用
python app.py
```

访问 http://localhost:5000

## 目录结构

```
corp-finance-analyzer/
├── app.py              # Flask 主应用
├── analyzer.py         # 分析引擎
├── requirements.txt    # Python 依赖
├── templates/
│   └── index.html     # 前端页面
├── static/
│   └── uploads/       # 上传文件目录
└── README.md
```
