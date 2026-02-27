#!/bin/bash
# 重启服务脚本

echo "🔄 重启公司金融年报分析系统..."

# 停止旧进程
pkill -f "gunicorn.*app:app" 2>/dev/null
pkill -f "python app.py" 2>/dev/null
sleep 2

# 启动 Gunicorn
cd /root/.openclaw/workspace/corp-finance-analyzer
source venv/bin/activate

nohup gunicorn \
    --workers 3 \
    --threads 2 \
    --timeout 120 \
    --bind 0.0.0.0:5000 \
    --access-logfile /tmp/gunicorn-access.log \
    --error-logfile /tmp/gunicorn-error.log \
    app:app &

sleep 3

# 检查状态
if curl -s http://localhost:5000/api/status | grep -q "running"; then
    echo "✅ 服务启动成功!"
    echo "🌐 访问地址：http://$(hostname -I | awk '{print $1}'):5000"
    echo "📋 查看日志：tail -f /tmp/gunicorn-error.log"
else
    echo "❌ 服务启动失败，请检查日志"
    tail -20 /tmp/gunicorn-error.log
fi
