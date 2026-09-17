# 🌟 元气桌面精灵 (Desktop Pet Companion) 🥂🫧

<p align="center">
  <img src="assets/pet_boy_sunshine.png" width="170" alt="Sunshine Photographer" />
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/pet_cheer.png" width="160" alt="Bubble Girl" />
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/pet_boy_hawaiian.png" width="160" alt="Hawaiian Boy" />
</p>

<p align="center">
  <strong>一款基于 Python & PyQt 开发的跨平台多角色高互动桌面精灵与伴侣系统</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version" />
  <img src="https://img.shields.io/badge/GUI-PyQt5-green.svg" alt="PyQt5" />
  <img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-orange.svg" alt="Platforms" />
  <img src="https://img.shields.io/badge/License-MIT-purple.svg" alt="License" />
</p>

---

## ✨ 项目亮点与功能 (Features)

- 🎭 **多角色与丰富造型随心切换 (Multi-Characters & Outfits)**：
  - **📷 阳光摄影少年 (全新精绘)**：治愈系开朗笑容、经典复古单反、热情挥手问候，充满少年元气！
  - **🌺 潮酷花衬衫少年 (全新精绘)**：新海诚/京阿尼画风、帅气黑框眼镜、热带粉衬衫与花领带、单手插兜自信微笑。
  - **🌸 泡泡元气少女 (Q版萌系)**：轻盈仙女裙、甜美举杯干杯（Cheers! 🥂）、眨眼微笑动作。
  - **✨ 泡泡仙女 (写真卡片)**：唯美浪漫的夜景浮动卡片。
  - **🛍️ 潮酷少年 (写真卡片)**：潮酷商场街拍写真卡片。
  - **☀️ 拱桥写真 (写真卡片)**：阳光下倚靠白石桥的治愈系摄影师写真卡片。
  - **支持随时右键自由挑选，或一键「🔄 快速切换下一造型」**！
- 🫧 **动态上升泡泡粒子系统**：
  - 身旁不断升腾起梦幻肥皂泡泡，鼠标点击即可将泡泡戳破，极具沉浸解压感。
- 🖱️ **极致丝滑交互**：
  - **滚轮无级缩放**：鼠标悬停在精灵上，滑动滚轮或触控板双指上下滑动，即可在 120px ~ 450px 自由缩放！
  - **自由拖拽**：鼠标按住身体任意部位可随心拖放停靠。
  - **单击互动**：触发跳跃举杯欢呼动作与定制鼓励台词气泡。
- 🍅 **科研与写代码生产力伴侣**：
  - **番茄工作法 (Pomodoro)**：右键或双击开启 25 分钟专注倒计时，精灵安静陪伴，结束后举杯庆祝。
  - **健康作息管家**：定时提醒喝水润喉、眼部放松、伸展活动；深夜智能提醒早点休息。
- 🖥️ **深度操作系统优化**：
  - **macOS 底层锁死防隐藏**：集成 Cocoa 原生底层属性，点击其他全屏或前台窗口绝不消失，跨所有虚拟桌面（Spaces）常驻。
  - **系统托盘集成**：屏幕顶部状态栏/任务栏图标，随时一键唤醒回最前层。

---

## 🚀 快速上手与运行 (Quick Start)

### 1. 克隆或下载本仓库
```bash
git clone https://github.com/YOUR_USERNAME/DesktopPet.git
cd DesktopPet
```

### 2. 安装依赖
建议使用 Python 3.8 及以上版本：
```bash
pip install -r requirements.txt
```

### 3. 运行桌面精灵
- **macOS / Linux**:
  ```bash
  python3 main.py
  ```
  或者后台守护模式运行（关闭终端也不退出）：
  ```bash
  bash run_daemon.sh
  ```
- **Windows**:
  ```cmd
  python main.py
  ```

---

## 📦 打包为独立免安装程序 (Packaging)

本项目完全支持使用 **PyInstaller** 打包成脱离 Python 环境的独立应用：

```bash
pip install pyinstaller
python3 build_app.py
```
- **macOS**: 将在 `dist/` 目录下生成 `DesktopPet.app`，直接拖入「应用程序」即可使用。
- **Windows**: 将在 `dist/` 目录下生成 `DesktopPet.exe`，双击即可直接运行，方便发给朋友！

---

## 🕹️ 快捷操作与交互指南 (Cheatsheet)

| 操作 | 对应功能 |
| :--- | :--- |
| **鼠标左键单击** | 触发举杯干杯庆祝动作（Cheers! 🥂）与打气台词 |
| **鼠标左键按住拖动** | 自由抓取并移动精灵到屏幕任意位置 |
| **鼠标悬停滚轮滚动** | **无级自由放大 / 缩小精灵尺寸** (120px ~ 450px) |
| **鼠标点击飘浮泡泡** | 戳破梦幻肥皂泡 🫧 |
| **鼠标双击** | 快速切换开启 25 分钟专注番茄钟 |
| **鼠标右键** | 唤出完整控制菜单（形态切换、尺寸预设、特效开关、置顶锁定、退出等） |
| **状态栏托盘图标** | 单击顶部菜单栏泡泡图标，瞬间将精灵拉回屏幕中央最前层 |

---

## 🎨 自定义指南 (Customization)

- **替换或增加立绘素材**：
  - 所有图片资源均位于 `assets/` 目录：
    - `pet_idle.png`：待机呼吸立绘（透明背景 PNG）
    - `pet_cheer.png`：点击欢呼/干杯动作立绘
    - `pet_photo_card.png`：照片卡片模式立绘
    - `bubble.png`：飘浮泡泡素材
  - 您可以直接放入自己的原创动漫角色、宠物猫狗照片或真人抠图进行替换！
- **修改或新增台词词库**：
  - 打开 `dialog_bubble.py`，编辑 `QUOTES` 字典中的文字，可以根据个人喜好添加专属台词、情侣纪念日问候、或实验室打气金句。

---

## 📂 项目文件结构 (Repository Layout)

```text
DesktopPet/
├── assets/                  # 美术立绘与动效贴图素材
│   ├── pet_idle.png         # Q版待机立绘
│   ├── pet_cheer.png        # Q版干杯立绘
│   ├── pet_photo_card.png   # 唯美照片卡片
│   ├── photo_original.jpg   # 原始参考照
│   └── bubble.png           # 梦幻肥皂泡泡
├── pet_widget.py            # 核心悬浮窗逻辑、泡泡粒子物理引擎与鼠标交互
├── dialog_bubble.py         # 漫画风气泡对话框与台词库
├── companion_timer.py       # 番茄工作法与作息健康提醒器
├── main.py                  # 主程序入口与系统托盘管理
├── build_app.py             # 独立应用打包脚本
├── run_daemon.sh            # 后台守护启动脚本
├── 启动桌面精灵.command      # macOS 访达一键双击运行脚本
├── requirements.txt         # 项目依赖清单
├── .gitignore               # Git 忽略配置
├── LICENSE                  # MIT 开源协议
└── README.md                # 项目文档
```

---

## 📄 开源许可证 (License)

本项目遵循 [MIT License](LICENSE) 开源协议。欢迎 Star ⭐️、Fork 与贡献代码！
