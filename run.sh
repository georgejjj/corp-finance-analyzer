#!/bin/bash
# 公司金融年报分析系统 - 运行脚本

echo "======================================"
echo "📊 公司金融年报分析系统"
echo "======================================"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python3"
    exit 1
fi

echo "✓ Python 版本：$(python3 --version)"

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ 未找到 pip3，请先安装 pip"
    echo "   运行：curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py"
    echo "        python3 get-pip.py"
    exit 1
fi

echo "✓ pip 版本：$(pip3 --version)"

# 创建必要目录
mkdir -p static/uploads

# 安装依赖
echo ""
echo "📦 安装依赖..."
pip3 install -r requirements.txt

# 检查 API Key
echo ""
if [ -f ".env" ]; then
    echo "✓ 发现 .env 配置文件"
else
    echo "⚠ 未发现 .env 文件，请复制 .env.example 并配置 API Key"
    echo "   cp .env.example .env"
    echo "   然后编辑 .env 文件，填入你的 DASHSCOPE_API_KEY"
fi

# 启动应用
echo ""
echo "======================================"
echo "🚀 启动应用..."
echo "======================================"
echo ""
echo "🌐 访问地址：http://localhost:5000"
echo "📁 上传目录：$(pwd)/static/uploads"
echo ""

python3 app.py
