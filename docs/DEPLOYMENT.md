# 部署指南

## 生产环境部署

### 1. 环境变量配置

**后端 .env 文件：**
```bash
# 必须使用强随机密钥
SECRET_KEY=<64 字符十六进制>
ENCRYPTION_KEY=<64 字符十六进制>

# 数据库
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/bidding

# 服务器
HOST=0.0.0.0
PORT=8000

# CORS (生产环境域名)
ALLOWED_ORIGINS=https://your-domain.com

# 日志
LOG_LEVEL=WARNING
```

**前端 .env 文件：**
```bash
VITE_API_BASE_URL=https://api.your-domain.com/api
VITE_ENCRYPTION_KEY=<与后端相同的 64 字符十六进制>
```

---

### 2. Docker Compose 部署 (推荐)

```bash
# 1. 生成密钥
python -c "import secrets; print(secrets.token_hex(32))"

# 2. 复制环境变量文件
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. 编辑 .env 文件，填入实际值

# 4. 启动服务
docker-compose up -d

# 5. 查看日志
docker-compose logs -f
```

---

### 3. Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL 证书
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # 前端静态文件
    location / {
        root /var/www/bidding-frontend;
        try_files $uri $uri/ /index.html;
    }
    
    # 后端 API 代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

### 4. SSL 证书 (Let's Encrypt)

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期 (已添加到 cron)
sudo certbot renew --dry-run
```

---

### 5. 数据库备份

```bash
# PostgreSQL 备份
pg_dump bidding > backup_$(date +%Y%m%d).sql

# 恢复
psql bidding < backup_20260305.sql

# 定时备份 (crontab)
0 2 * * * pg_dump bidding > /backups/bidding_$(date +\%Y\%m\%d).sql
```

---

### 6. 监控与日志

**健康检查端点：**
```bash
curl https://api.your-domain.com/health
# 返回：{"status": "healthy"}
```

**日志查看：**
```bash
# 后端日志
docker-compose logs -f backend

# Nginx 日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

### 7. 安全加固清单

- [ ] 修改所有默认密钥
- [ ] 启用 HTTPS (强制)
- [ ] 配置防火墙 (仅开放 80/443)
- [ ] 数据库使用强密码
- [ ] 定期更新系统包
- [ ] 配置日志轮转
- [ ] 设置监控告警
- [ ] 定期备份数据

---

## 故障排查

### 常见问题

**1. 后端启动失败**
```bash
# 检查环境变量
cat backend/.env

# 检查端口占用
lsof -i :8000

# 查看日志
docker-compose logs backend
```

**2. 前端无法连接后端**
```bash
# 检查 API 地址配置
cat frontend/.env

# 检查 CORS 配置
cat backend/.env | grep ALLOWED_ORIGINS
```

**3. 数据库连接失败**
```bash
# 测试连接
psql -h localhost -U user -d bidding

# 检查 PostgreSQL 状态
systemctl status postgresql
```

---

_最后更新：2026-03-05_
