# -*- coding: utf-8 -*-
"""
Desktop Pet Main Launcher
Coordinates system tray, QApplication lifecycle, and loads DesktopPetWidget.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

from pet_widget import DesktopPetWidget


def create_tray_icon(app, pet_widget, assets_dir):
    """Create a system tray icon for quick control and status."""
    tray = QSystemTrayIcon(pet_widget)

    icon_path = os.path.join(assets_dir, "bubble.png")
    if os.path.exists(icon_path):
        tray.setIcon(QIcon(icon_path))
    else:
        # Fallback
        pix = QPixmap(32, 32)
        pix.fill(Qt.transparent)
        tray.setIcon(QIcon(pix))

    tray_menu = QMenu()
    tray_menu.setStyleSheet("""
        QMenu {
            font-family: 'PingFang SC', sans-serif;
            font-size: 13px;
        }
    """)

    def bring_to_front():
        pet_widget.show()
        pet_widget.raise_()
        pet_widget.activateWindow()
        pet_widget.trigger_cheer(quote="我在这里哦！🥂✨")

    act_show = tray_menu.addAction("✨ 显示/唤醒桌面精灵")
    act_show.triggered.connect(bring_to_front)

    act_cheer = tray_menu.addAction("🥂 干杯互动")
    act_cheer.triggered.connect(pet_widget.trigger_cheer)

    tray_menu.addSeparator()

    act_quit = tray_menu.addAction("❌ 退出程序")
    act_quit.triggered.connect(app.quit)

    tray.setContextMenu(tray_menu)
    tray.setToolTip("桌面精灵 - 你的元气陪伴助手")

    def on_tray_activated(reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            bring_to_front()
    tray.activated.connect(on_tray_activated)

    tray.show()
    return tray


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DesktopPet")
    app.setQuitOnLastWindowClosed(False)

    if getattr(sys, "frozen", False):
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")

    # Instantiate and display pet
    pet = DesktopPetWidget(assets_dir=assets_dir)
    pet.show()
    pet.raise_()
    pet.activateWindow()

    # System tray setup
    tray = create_tray_icon(app, pet, assets_dir)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
