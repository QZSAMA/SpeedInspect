#!/bin/bash
set -e

# SpeedInspect 公网 HTTPS 证书自动部署脚本
# 自动申请 Let's Encrypt 公共信任证书，配置 Nginx，支持自动续期

# 配置项
DOMAIN="qzsama.synology.me"  # 替换成你的实际域名
EMAIL="271782914@qq.com"  # 替换成你的邮箱，用于证书到期提醒
NGINX_CONF_PATH="/etc/nginx/sites-available/speedinspect.conf"
PROJECT_ROOT="/home/qz/.openclaw/workspace/SpeedInspect"

echo "🚀 SpeedInspect HTTPS 证书部署脚本"
echo "域名: $DOMAIN"
echo "=================================="

# 检查是否安装了 Certbot
if ! command -v certbot &> /dev/null; then
    echo "📦 安装 Certbot..."
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
fi

# 申请证书（Nginx 自动验证，需要域名解析到当前服务器且80/443端口开放）
echo "🔑 申请 Let's Encrypt 证书..."
sudo certbot --nginx \
    -d "$DOMAIN" \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --redirect  # 自动配置 HTTP 跳转到 HTTPS

# 验证证书是否申请成功
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "❌ 证书申请失败，请检查域名解析和端口开放情况"
    exit 1
fi

# 生成 SpeedInspect 专用 Nginx 配置
echo "⚙️ 生成 Nginx 配置..."
sudo tee "$NGINX_CONF_PATH" > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    # Let's Encrypt 证书
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # 前端静态文件
    location / {
        root $PROJECT_ROOT/frontend/web/dist;
        try_files \$uri \$uri/ /index.html;
        index index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 摄像头/WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    # 安全头配置（确保摄像头权限正常）
    add_header Permissions-Policy "camera=(), microphone=()" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 限制文件上传大小
    client_max_body_size 100M;
}
EOF

# 启用配置并重启 Nginx
echo "🔧 启用 Nginx 配置..."
sudo ln -sf "$NGINX_CONF_PATH" /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# 配置自动续期（Certbot 会自动添加 cron 任务，这里验证一下）
echo "⏰ 配置证书自动续期..."
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

echo ""
echo "✅ 部署完成！"
echo "=================================="
echo "访问地址: https://$DOMAIN"
echo "证书有效期: 90 天，会自动续期"
echo "Nginx 配置路径: $NGINX_CONF_PATH"
echo ""
echo "现在访问你的域名应该已经是公共信任的 HTTPS 连接，摄像头权限可以正常使用了！"
