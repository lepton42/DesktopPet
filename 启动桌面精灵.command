#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# 检查是否已在运行
PID=$(pgrep -f "python3.*DesktopPet/main.py" | head -n 1)

if [ -z "$PID" ]; then
    nohup python3 main.py >/dev/null 2>&1 &
fi

# 给出通知弹窗
osascript -e 'display notification "桌面精灵已在右下角准备就绪，点击右上角状态栏泡泡图标可随时唤醒！" with title "桌面精灵 🥂"'
