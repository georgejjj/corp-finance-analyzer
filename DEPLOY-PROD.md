# 生产环境部署指南

## 📊 两种部署方式对比

### 方式一：Flask 开发服务器（当前使用）

```bash
python3 app.py
# 或
./run.sh
```

**特点：**
- ✅ 快速启动，适合演示/测试
- ✅ 调试模式，代码变更自动重载
- ❌ 单线程，并发能力差
- ❌ 性能无优化
- ❌ 不适合长期运行

**适用场景：** 本地开发、教学演示、临时测试

---

### 方式二：Gunicorn + Nginx（生产环境）

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动（4 个 worker 进程）
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

**架构：**
```
用户请求 → Nginx (80 端口) → Gunicorn (多进程) → Flask 应用
              ↓
         静态文件缓存
```

**特点：**
- ✅ 多进程并发处理
- ✅ 自动崩溃恢复
- ✅ Nginx 处理静态文件（高效）
- ✅ 支持 HTTPS、负载均衡
- ✅ 适合长期稳定运行

**适用场景：** 正式对外服务、多用户访问

---

## 🔧 快速生产部署（3 步）

### 1. 安装 Gunicorn

```bash
cd /root/.openclaw/workspace/corp-finance-analyzer
source venv/bin/activate
pip install gunicorn
```

### 2. 启动服务

```bash
# 后台运行（4 个 worker）
gunicorn --workers 4 --bind 0.0.0.0:5000 --daemon app:app

# 或前台运行（方便调试）
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

### 3. 配置防火墙/安全组

在腾讯云控制台开放端口：
- 端口：`5000`
- 协议：`TCP`
- 来源：`0.0.0.0/0`

---

## 📝 完整生产部署（systemd + Nginx）

执行自动化脚本：

```bash
chmod +x deploy-prod.sh
./deploy-prod.sh
```

这将配置：
- ✅ systemd 服务（开机自启、崩溃恢复）
- ✅ Nginx 反向代理
- ✅ 日志管理

---

## 🔍 常用命令

```bash
# 查看服务状态
systemctl status finance-analyzer

# 查看日志
journalctl -u finance-analyzer -f

# 重启服务
systemctl restart finance-analyzer

# 停止服务
systemctl stop finance-analyzer

# Nginx 配置测试
nginx -t

# 重新加载 Nginx
systemctl reload nginx
```

---

## 📈 性能对比

| 指标 | Flask 开发 | Gunicorn (4 workers) |
|------|-----------|---------------------|
| 并发请求 | ~10 req/s | ~100+ req/s |
| 响应时间 | 较慢 | 快 |
| CPU 利用 | 单核 | 多核 |
| 稳定性 | 易崩溃 | 自动恢复 |

---

## 💡 建议

**当前演示场景：** 保持 Flask 开发服务器即可

**正式使用时：** 升级到 Gunicorn + Nginx
