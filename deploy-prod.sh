#!/bin/bash
# 公司金融年报分析系统 - 生产环境部署脚本

set -e

echo "======================================"
echo "📊 生产环境部署"
echo "======================================"

APP_DIR="/root/.openclaw/workspace/corp-finance-analyzer"
VENV_DIR="$APP_DIR/venv"
SOCK_FILE="$APP_DIR/gunicorn.sock"
LOG_DIR="$APP_DIR/logs"

# 1. 创建日志目录
mkdir -p "$LOG_DIR"

# 2. 创建/激活虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# 3. 安装/更新依赖
echo "📦 安装生产依赖..."
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt"
pip install gunicorn  # 生产级 WSGI 服务器

# 4. 创建 systemd 服务文件
echo "⚙️ 配置 systemd 服务..."
cat > /etc/systemd/system/finance-analyzer.service << EOF
[Unit]
Description=公司金融年报分析系统
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn --workers 4 --bind unix:$SOCK_FILE app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 5. 配置 Nginx
echo "🌐 配置 Nginx..."
cat > /etc/nginx/conf.d/finance-analyzer.conf << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        include proxy_params;
        proxy_pass http://unix:/root/.openclaw/workspace/corp-finance-analyzer/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件由 Nginx 直接处理
    location /static {
        alias /root/.openclaw/workspace/corp-finance-analyzer/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 上传文件限制
    client_max_body_size 50M;
}
EOF

# 6. 启动服务
echo "🚀 启动服务..."
systemctl daemon-reload
systemctl enable finance-analyzer
systemctl restart finance-analyzer
systemctl restart nginx

# 7. 检查状态
echo ""
echo "======================================"
echo "✅ 部署完成!"
echo "======================================"
echo ""
systemctl status finance-analyzer --no-pager | head -10
echo ""
echo "🌐 访问地址：http://$(hostname -I | awk '{print $1}')"
echo "📋 查看日志：journalctl -u finance-analyzer -f"
echo "⏹️  停止服务：systemctl stop finance-analyzer"
echo "🔄 重启服务：systemctl restart finance-analyzer"
