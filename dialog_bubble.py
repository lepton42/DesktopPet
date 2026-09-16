# -*- coding: utf-8 -*-
"""
Desktop Pet Speech Bubble Module
Provides a stylized cartoon/comic speech bubble with quotes for study, coding, and companionship.
"""

import random
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPainterPath
from PyQt5.QtWidgets import QWidget

QUOTES = {
    "cheer": [
        "来！跟我一起干杯！Cheers~ 🥂",
        "今天辛苦啦，歇会儿喝口水吧！🥤",
        "继续加油，代码一定能一次跑通的！✨",
        "哎呀，戳到我啦！(๑•̀ㅂ•́)و✧",
        "捕捉到一只努力的科研人！太棒啦~ 🌟",
        "有我陪着你，写代码一点都不孤单哦！💖",
        "累了就看看窗外，今天也是闪闪发光的一天！✨",
        "咕咚咕咚~ 冰镇汽水最治愈啦！🍾",
        "所有的 Bug 都已经被施加了消散魔法！🪄",
        "无论遇到什么难题，慢慢理清思路就好啦！💪",
    ],
    "cheer_boy": [
        "哟！写代码辛苦啦，给你比个耶 ✌️！",
        "今天这套粉色花衬衫够不够帅气？😎",
        "咔嚓！📷 抓拍到一个超级专注的学霸！",
        "遇到 Bug 别慌，稳住心态咱们能赢！💪",
        "走，歇会儿去喝杯咖啡/冰阔落！☕",
        "搞定这个模型，今天又是大满贯！🎯",
        "阳光正好，深呼吸一下，满血复活！☀️",
        "保持热爱，奔赴山海！今天也要元气满满！🔥",
    ],
    "health": [
        "已经专注好一会儿啦，伸个懒腰放松一下背部吧~ 🧘‍♀️",
        "滴！喝水提醒：小口喝点温水润润喉咙哦~ 💧",
        "眨眨眼，转动一下眼球，保护明亮的眼睛！👀",
        "站起来活动一下手腕和肩膀吧~ 🍃",
    ],
    "night": [
        "夜深啦，窗外的月色真美，别熬太晚哦~ 🌙",
        "今天任务完成得很棒，准备好好睡个美容觉吧！🛌",
        "星光不问赶路人，但好好休息明天才更有精神哦！⭐",
    ],
    "pomodoro_start": [
        "专注模式启动！25分钟里我会安安静静陪着你，冲鸭！🍅",
        "开启深度工作状态~ 手机放一边，沉浸式写代码吧！💻",
    ],
    "pomodoro_end": [
        "叮！25分钟专注圆满达成！🎉 太厉害了，快举杯犒劳一下自己！🥂",
        "完美收官！站起来走动5分钟，享受一下胜利的喜悦~ 🎈",
    ]
}


class DialogBubble(QWidget):
    """A floating comic-style speech bubble attached to the pet."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        self.text = ""
        self.fade_timer = QTimer(self)
        self.fade_timer.setSingleShot(True)
        self.fade_timer.timeout.connect(self.hide)

        self.setFixedSize(260, 110)

    def show_message(self, text=None, category="cheer", duration_ms=4500):
        """Display a message bubble."""
        if text is None:
            quotes_list = QUOTES.get(category, QUOTES["cheer"])
            text = random.choice(quotes_list)

        self.text = text
        self.update()
        self.show()
        self.raise_()

        self.fade_timer.stop()
        self.fade_timer.start(duration_ms)

    def paintEvent(self, event):
        if not self.text:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width() - 14
        h = self.height() - 22
        corner_radius = 16

        # Draw soft shadow
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(QRectF(9, 9, w, h), corner_radius, corner_radius)
        painter.fillPath(shadow_path, QColor(0, 0, 0, 35))

        # Main speech bubble body (soft pearlescent pinkish-white)
        bubble_path = QPainterPath()
        rect = QRectF(6, 6, w, h)
        bubble_path.addRoundedRect(rect, corner_radius, corner_radius)

        # Draw triangle pointer (pointing downwards towards pet)
        pointer_x = 45
        bubble_path.moveTo(pointer_x, 6 + h)
        bubble_path.lineTo(pointer_x - 12, 6 + h + 14)
        bubble_path.lineTo(pointer_x + 14, 6 + h)
        bubble_path.closeSubpath()

        # Fill background
        painter.setBrush(QBrush(QColor(255, 252, 253, 245)))
        painter.setPen(QPen(QColor(255, 185, 210, 230), 2))
        painter.drawPath(bubble_path)

        # Text rendering
        painter.setPen(QColor(60, 40, 50))
        font = QFont()
        font.setFamilies(["PingFang SC", "Microsoft YaHei", "WenQuanYi Micro Hei", "Segoe UI", "sans-serif"])
        font.setPointSize(11)
        font.setWeight(QFont.Medium)
        painter.setFont(font)

        text_rect = QRectF(18, 14, w - 24, h - 16)
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter | Qt.TextWordWrap, self.text)
