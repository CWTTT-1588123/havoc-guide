#!/usr/bin/env bash
# 海克斯大乱斗攻略站 —— 服务器一键部署（Ubuntu 22.04）
# 用法：把整个站点目录传到服务器后，cd 到该目录，执行： bash setup.sh
set -e
cd "$(dirname "$0")"

# 非交互：避免"Daemons using outdated libraries"等 apt/needrestart 交互弹窗
export DEBIAN_FRONTEND=noninteractive
if [ -d /etc/needrestart ]; then
  echo 'NEEDRESTART_MODE=a' | sudo tee /etc/needrestart/conf.d/99auto.conf >/dev/null 2>&1 || true
fi

echo "==> 1/4 安装 Python3 + venv"
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip

echo "==> 2/4 创建虚拟环境并安装依赖"
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

echo "==> 3/4 配置 systemd 常驻服务"
SERVICE_DIR="$(pwd)"
sudo tee /etc/systemd/system/havoc-guide.service >/dev/null <<EOF
[Unit]
Description=Havoc Guide
After=network.target

[Service]
User=root
WorkingDirectory=$SERVICE_DIR
Environment=PATCH_VERSION=16.16
Environment=DRAGON_VER=16.17.1
ExecStart=$SERVICE_DIR/.venv/bin/uvicorn webapp:app --host 0.0.0.0 --port 8000 --workers 1
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now havoc-guide

echo "==> 4/4 完成，检查状态"
sleep 1
sudo systemctl status havoc-guide --no-pager || true
echo ""
echo "本地访问(测试)： curl http://127.0.0.1:8000"
echo "公网访问： http://公网IP:8000  (记得防火墙/安全组放行 8000)"
echo "停止： sudo systemctl stop havoc-guide    启动： sudo systemctl start havoc-guide"
