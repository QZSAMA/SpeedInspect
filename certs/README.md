# 自签名证书目录

## 说明
- 本目录用于存放开发测试用的自签名证书
- `server.crt` 和 `server.key` 不会被提交到 Git（已在 .gitignore 中配置）
- 生产环境请使用正规CA颁发的证书

## 生成证书
执行脚本自动生成：
```bash
./scripts/generate-cert.sh [你的域名]
```

默认域名: qzsama.synology.me

## Nginx 配置参考
见 `docs/nginx-self-signed.conf`

## 客户端信任
1. 下载 server.crt 到本地
2. 安装到系统受信任的根证书颁发机构
3. 重启浏览器即可消除安全警告
