#!/bin/bash
# 一键常驻启动桌面精灵（关闭终端也不受影响）
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# 检查是否已在运行
PID=$(pgrep -f "python3.*DesktopPet/main.py" | head -n 1)

if [ -n "$PID" ]; then
    echo "桌面精灵已在后台运行中 (PID: $PID) ✨"
else
    nohup python3 main.py >/dev/null 2>&1 &
    NEW_PID=$!
    echo "桌面精灵已成功在后台启动 (PID: $NEW_PID) 🥂"
fi
