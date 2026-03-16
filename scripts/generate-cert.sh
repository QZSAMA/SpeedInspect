#!/bin/bash
# 自签名证书生成脚本
# 使用方法: ./scripts/generate-cert.sh [域名]

DEFAULT_DOMAIN="qzsama.synology.me"
DOMAIN=${1:-$DEFAULT_DOMAIN}

CERT_DIR="$(dirname "$0")/../certs"
mkdir -p "$CERT_DIR"

echo "生成自签名证书，域名: $DOMAIN"
echo "证书有效期: 365天"

openssl req -x509 -newkey rsa:4096 \
  -keyout "$CERT_DIR/server.key" \
  -out "$CERT_DIR/server.crt" \
  -days 365 -nodes \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=SpeedInspect/OU=Development/CN=$DOMAIN"

if [ $? -eq 0 ]; then
  echo ""
  echo "✅ 证书生成成功!"
  echo "证书路径: $CERT_DIR/"
  echo "公钥: server.crt"
  echo "私钥: server.key"
  echo ""
  echo "Nginx 配置参考:"
  echo "  ssl_certificate $CERT_DIR/server.crt;"
  echo "  ssl_certificate_key $CERT_DIR/server.key;"
else
  echo "❌ 证书生成失败"
  exit 1
fi
