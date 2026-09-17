# -*- coding: utf-8 -*-
"""
Desktop Pet Core Widget
Implements the transparent, animated, draggable desktop sprite with bubble particles and interactions.
"""

import os
import math
import random
from PyQt5.QtCore import Qt, QTimer, QPoint, QRectF
from PyQt5.QtGui import QPainter, QPixmap, QColor, QPen, QBrush, QCursor
from PyQt5.QtWidgets import QWidget, QMenu, QAction

from dialog_bubble import DialogBubble
from companion_timer import CompanionTimer


def make_window_persistent_macos(qt_widget):
    """Ensure window stays visible across all macOS spaces, floating above normal windows, and never hides on deactivate."""
    try:
        import objc
        from Cocoa import (
            NSWindowCollectionBehaviorCanJoinAllSpaces,
            NSWindowCollectionBehaviorFullScreenAuxiliary,
        )
        nsview = objc.objc_object(c_void_p=int(qt_widget.winId()))
        nswindow = nsview.window()
        if nswindow:
            if hasattr(nswindow, 'setHidesOnDeactivate_'):
                nswindow.setHidesOnDeactivate_(False)
            if hasattr(nswindow, 'setCanHide_'):
                nswindow.setCanHide_(False)
            if hasattr(nswindow, 'setLevel_'):
                nswindow.setLevel_(3)  # NSFloatingWindowLevel
            behavior = NSWindowCollectionBehaviorCanJoinAllSpaces | NSWindowCollectionBehaviorFullScreenAuxiliary
            nswindow.setCollectionBehavior_(behavior)
    except Exception:
        pass


class BubbleParticle:
    """A floating soap bubble matching the original photo's ambient bubble effect."""

    def __init__(self, bounds_w, bounds_h):
        self.bounds_w = bounds_w
        self.bounds_h = bounds_h
        self.reset(random_y=True)

    def reset(self, random_y=False):
        self.x = random.uniform(20, self.bounds_w - 20)
        self.y = random.uniform(20, self.bounds_h) if random_y else self.bounds_h + random.uniform(5, 30)
        self.radius = random.uniform(8, 22)
        self.vy = random.uniform(0.6, 1.8)
        self.vx_amp = random.uniform(0.3, 0.8)
        self.phase = random.uniform(0, math.pi * 2)
        self.phase_speed = random.uniform(0.02, 0.05)
        self.alpha = random.uniform(120, 210)
        self.is_popped = False

    def update(self):
        if self.is_popped:
            return

        self.phase += self.phase_speed
        self.x += math.sin(self.phase) * self.vx_amp
        self.y -= self.vy

        # Out of screen at top -> reset to bottom
        if self.y < -self.radius * 2 or self.x < -20 or self.x > self.bounds_w + 20:
            self.reset()

    def check_pop(self, mx, my):
        """Check if mouse pointer poked this bubble."""
        dist = math.hypot(self.x - mx, self.y - my)
        if dist <= self.radius + 6:
            self.is_popped = True
            return True
        return False


class DesktopPetWidget(QWidget):
    """Main Desktop Pet Window."""

    STYLE_BOY_SUNSHINE = "boy_sunshine"
    STYLE_BOY_HAWAIIAN = "boy_hawaiian"
    STYLE_GIRL_CHIBI = "girl_chibi"
    STYLE_GIRL_CARD = "girl_card"
    STYLE_BOY_HAWAIIAN_CARD = "boy_hawaiian_card"
    STYLE_BOY_SUNSHINE_CARD = "boy_sunshine_card"

    ALL_STYLES = [
        STYLE_BOY_SUNSHINE,
        STYLE_BOY_HAWAIIAN,
        STYLE_GIRL_CHIBI,
        STYLE_GIRL_CARD,
        STYLE_BOY_HAWAIIAN_CARD,
        STYLE_BOY_SUNSHINE_CARD,
    ]

    STATE_IDLE = "idle"
    STATE_CHEER = "cheer"

    def __init__(self, assets_dir):
        super().__init__()
        self.assets_dir = assets_dir

        # Window properties: Frameless, transparent background, always on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)

        # Pet states & appearance (default to the newly regenerated sunshine boy!)
        self.current_style = self.STYLE_BOY_SUNSHINE
        self.current_state = self.STATE_IDLE
        self.target_width = 220
        self.enable_bubbles = True

        # Motion & Animation
        self.float_phase = 0.0
        self.bounce_offset = 0.0
        self.drag_start_pos = None
        self.has_dragged = False

        # Load Sprite Images
        self.pixmaps = {}
        self.load_assets()

        # Bubble Particles (photo atmosphere)
        self.bubbles = []
        self.init_bubbles()

        # Dialog Bubble
        self.dialog = DialogBubble()

        # Companion Timers (Pomodoro & Care)
        self.companion = CompanionTimer(self)
        self.companion.reminder_triggered.connect(self._on_reminder)
        self.companion.pomodoro_tick.connect(self._on_pomodoro_tick)

        # Animation & Physics Timers
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(33)  # ~30 FPS
        self.anim_timer.timeout.connect(self._on_anim_frame)
        self.anim_timer.start()

        # Cheer recovery timer (returns to idle after 2.5s)
        self.state_timer = QTimer(self)
        self.state_timer.setSingleShot(True)
        self.state_timer.timeout.connect(self._return_to_idle)

        # Ambient self-dialogue timer (random cute speech every 3-5 mins)
        self.ambient_speech_timer = QTimer(self)
        self.ambient_speech_timer.setInterval(180 * 1000)
        self.ambient_speech_timer.timeout.connect(self._on_ambient_speech)
        self.ambient_speech_timer.start()

        # Set initial size and position (bottom-right desktop area)
        self.update_geometry_size()
        self.move_to_default_position()

        # Initial cheerful greeting
        QTimer.singleShot(800, lambda: self.trigger_cheer(quote="哈喽！我是你的桌面精灵，今天也一起加油吧！🥂"))

    def showEvent(self, event):
        super().showEvent(event)
        make_window_persistent_macos(self)
        if hasattr(self, "dialog"):
            make_window_persistent_macos(self.dialog)

    def load_assets(self):
        """Load pixmaps for all chibi characters and photo cards."""
        assets_map = {
            "boy_sunshine": "pet_boy_sunshine.png",
            "boy_hawaiian": "pet_boy_hawaiian.png",
            "girl_idle": "pet_idle.png",
            "girl_cheer": "pet_cheer.png",
            "girl_card": "pet_photo_card.png",
            "boy_hawaiian_card": "pet_boy_hawaiian_card.png",
            "boy_sunshine_card": "pet_boy_sunshine_card.png",
            "bubble": "bubble.png",
        }
        for key, fname in assets_map.items():
            fpath = os.path.join(self.assets_dir, fname)
            if os.path.exists(fpath):
                self.pixmaps[key] = QPixmap(fpath)

    def init_bubbles(self):
        """Create floating bubble particles."""
        self.bubbles.clear()
        w, h = self.width(), self.height()
        count = 14
        for _ in range(count):
            self.bubbles.append(BubbleParticle(w, h))

    def get_active_pixmap(self):
        """Retrieve current active pixmap based on style and animation state."""
        if self.current_style == self.STYLE_BOY_SUNSHINE:
            return self.pixmaps.get("boy_sunshine")
        elif self.current_style == self.STYLE_BOY_HAWAIIAN:
            return self.pixmaps.get("boy_hawaiian")
        elif self.current_style == self.STYLE_GIRL_CHIBI:
            if self.current_state == self.STATE_CHEER:
                return self.pixmaps.get("girl_cheer") or self.pixmaps.get("girl_idle")
            return self.pixmaps.get("girl_idle")
        elif self.current_style == self.STYLE_GIRL_CARD:
            return self.pixmaps.get("girl_card")
        elif self.current_style == self.STYLE_BOY_HAWAIIAN_CARD:
            return self.pixmaps.get("boy_hawaiian_card")
        elif self.current_style == self.STYLE_BOY_SUNSHINE_CARD:
            return self.pixmaps.get("boy_sunshine_card")
        return None

    def update_geometry_size(self):
        """Recalculate window dimensions preserving true natural character aspect ratio."""
        pix = self.get_active_pixmap()
        char_w = self.target_width
        if pix and not pix.isNull() and pix.width() > 0:
            aspect = pix.height() / pix.width()
        else:
            aspect = 1.4

        char_h = int(char_w * aspect)

        # Margins for bubbles and soft shadow
        margin_x = 60
        margin_y = 50

        total_w = char_w + margin_x * 2
        total_h = char_h + margin_y * 2
        self.char_rect = QRectF(margin_x, margin_y, char_w, char_h)
        self.resize(total_w, total_h)

        for b in self.bubbles:
            b.bounds_w = total_w
            b.bounds_h = total_h

        self.update_dialog_position()

    def move_to_default_position(self):
        """Position the pet near bottom right of current screen."""
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        init_x = screen.width() - self.width() - 80
        init_y = screen.height() - self.height() - 90
        self.move(max(20, init_x), max(20, init_y))
        self.update_dialog_position()

    def update_dialog_position(self):
        """Sync dialogue bubble location above the pet."""
        if hasattr(self, "dialog"):
            bubble_x = self.x() + int(self.char_rect.x()) - 10
            bubble_y = self.y() + int(self.char_rect.y()) - self.dialog.height() + 5
            self.dialog.move(bubble_x, bubble_y)

    def trigger_cheer(self, quote=None):
        """Trigger cheerful reaction."""
        self.current_state = self.STATE_CHEER
        self.bounce_offset = -18.0  # Little jump
        self.update()

        self.state_timer.stop()
        self.state_timer.start(3000)

        cat = "cheer_boy" if "boy" in self.current_style else "cheer"
        self.dialog.show_message(text=quote, category=cat)

    def _return_to_idle(self):
        self.current_state = self.STATE_IDLE
        self.bounce_offset = 0.0
        self.update()

    def _on_reminder(self, category, msg):
        self.trigger_cheer(quote=msg if msg else None)
        if category == "pomodoro_end":
            # Spawn extra celebration bubbles!
            for b in self.bubbles:
                b.reset(random_y=True)

    def _on_pomodoro_tick(self, remaining_sec):
        # Update tooltip with remaining time
        mins = remaining_sec // 60
        secs = remaining_sec % 60
        self.setToolTip(f"🍅 专注陪伴中: {mins:02d}:{secs:02d}")

    def _on_ambient_speech(self):
        if self.current_state == self.STATE_IDLE:
            cat = "cheer_boy" if "boy" in self.current_style else "cheer"
            self.dialog.show_message(category=cat, duration_ms=4000)

    def _on_anim_frame(self):
        """30 FPS animation loop."""
        # Gentle hover oscillation
        self.float_phase += 0.06
        if self.float_phase > math.pi * 2:
            self.float_phase -= math.pi * 2

        # Recover bounce offset smoothly towards 0
        if self.bounce_offset < 0:
            self.bounce_offset += 1.8
            if self.bounce_offset > 0:
                self.bounce_offset = 0

        # Update bubble physics
        if self.enable_bubbles:
            for b in self.bubbles:
                b.update()

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # 1. Render Background Floating Bubbles
        if self.enable_bubbles:
            bubble_pix = self.pixmaps.get("bubble")
            for b in self.bubbles:
                if b.is_popped:
                    continue
                if bubble_pix:
                    painter.setOpacity(b.alpha / 255.0)
                    r = b.radius
                    painter.drawPixmap(QRectF(b.x - r, b.y - r, r * 2, r * 2).toRect(), bubble_pix)
                else:
                    # Fallback procedural bubble
                    painter.setPen(QPen(QColor(230, 245, 255, int(b.alpha)), 2))
                    painter.setBrush(QBrush(QColor(200, 230, 255, int(b.alpha * 0.25))))
                    painter.drawEllipse(QPointF(b.x, b.y), b.radius, b.radius)

        painter.setOpacity(1.0)

        # 2. Select Sprite Pixmap & Render with Strict Natural Aspect Ratio
        active_pix = self.get_active_pixmap()
        if active_pix and not active_pix.isNull():
            pw = active_pix.width()
            ph = active_pix.height()
            aspect = ph / pw if pw > 0 else 1.0

            # Scale within char_rect keeping true aspect ratio (no stretch / squash)
            scaled_w = self.char_rect.width()
            scaled_h = scaled_w * aspect
            if scaled_h > self.char_rect.height():
                scaled_h = self.char_rect.height()
                scaled_w = scaled_h / aspect

            hover_y = math.sin(self.float_phase) * 5.0 + self.bounce_offset
            draw_x = self.char_rect.x() + (self.char_rect.width() - scaled_w) / 2.0
            draw_y = self.char_rect.y() + (self.char_rect.height() - scaled_h) + hover_y

            # Draw subtle ground shadow beneath the character feet
            shadow_w = scaled_w * 0.6
            shadow_h = 13
            shadow_x = draw_x + (scaled_w - shadow_w) / 2.0
            shadow_y = self.char_rect.y() + self.char_rect.height() - 4
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(0, 0, 0, 32)))
            painter.drawEllipse(QRectF(shadow_x, shadow_y, shadow_w, shadow_h))

            # Draw pet sprite with perfect natural proportions
            target_rect = QRectF(draw_x, draw_y, scaled_w, scaled_h)
            painter.drawPixmap(target_rect.toRect(), active_pix)

    # Mouse & Drag Interactions
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.globalPos() - self.frameGeometry().topLeft()
            self.has_dragged = False
            event.accept()

            # Check if clicked on a bubble to pop it!
            if self.enable_bubbles:
                for b in self.bubbles:
                    if b.check_pop(event.pos().x(), event.pos().y()):
                        break

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_start_pos is not None:
            new_pos = event.globalPos() - self.drag_start_pos
            self.move(new_pos)
            self.has_dragged = True
            self.update_dialog_position()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.has_dragged:
                # Clicked on pet!
                self.trigger_cheer()
            self.drag_start_pos = None
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Double click -> toggle focus timer or cheer
            if not self.companion.is_pomodoro_active():
                self.start_pomodoro()
            else:
                self.trigger_cheer(quote="专注时光很宝贵，继续加油哦！💪")
            event.accept()

    def wheelEvent(self, event):
        """Scroll wheel or trackpad scroll over pet to smoothly zoom in/out."""
        delta = event.angleDelta().y()
        if delta != 0:
            step = 16 if delta > 0 else -16
            new_w = max(120, min(450, self.target_width + step))
            if new_w != self.target_width:
                self.set_character_width(new_w)
            event.accept()

    def contextMenuEvent(self, event):
        """Right-click context menu."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(255, 255, 255, 0.96);
                border: 1px solid rgba(255, 180, 200, 0.7);
                border-radius: 12px;
                padding: 6px;
                font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
                font-size: 13px;
                color: #333333;
            }
            QMenu::item {
                padding: 7px 22px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: #ffe6ef;
                color: #d6336c;
            }
            QMenu::separator {
                height: 1px;
                background: #f0d0dc;
                margin: 4px 8px;
            }
        """)

        action_poke = menu.addAction("💖 戳一戳互动")
        action_cheer = menu.addAction("🥂 举杯/比耶欢呼！")
        menu.addSeparator()

        # Multi-Character & Style Submenu
        style_menu = menu.addMenu("🎭 角色与造型切换")
        act_b_sunshine = style_menu.addAction("📷 阳光摄影少年 (全新精绘)")
        act_b_hawaiian = style_menu.addAction("🌺 潮酷花衬衫少年 (全新精绘)")
        act_g_chibi = style_menu.addAction("🌸 泡泡元气少女 (Q版萌系)")
        style_menu.addSeparator()
        act_g_card = style_menu.addAction("✨ 泡泡仙女 (写真卡片)")
        act_b_card1 = style_menu.addAction("🛍️ 潮酷少年 (写真卡片)")
        act_b_card2 = style_menu.addAction("☀️ 拱桥写真 (写真卡片)")

        action_next_style = menu.addAction("🔄 快速切换下一造型")

        # Bubble particles toggle
        bubble_text = "🫧 关闭飘浮泡泡" if self.enable_bubbles else "🫧 开启飘浮泡泡"
        action_toggle_bubbles = menu.addAction(bubble_text)

        # Size submenu
        size_menu = menu.addMenu("📐 调整尺寸大小")
        action_size_s = size_menu.addAction("小巧 (160px)")
        action_size_m = size_menu.addAction("标准 (220px)")
        action_size_l = size_menu.addAction("醒目 (280px)")
        action_size_xl = size_menu.addAction("特大 (340px)")
        menu.addSeparator()

        # Pomodoro
        if self.companion.is_pomodoro_active():
            action_pomodoro = menu.addAction("🍅 取消专注番茄钟")
        else:
            action_pomodoro = menu.addAction("🍅 开启专注番茄钟 (25分钟)")

        # Always on top
        is_stay_on_top = bool(self.windowFlags() & Qt.WindowStaysOnTopHint)
        top_text = "📌 取消置顶" if is_stay_on_top else "📌 保持置顶"
        action_toggle_top = menu.addAction(top_text)

        menu.addSeparator()
        action_quit = menu.addAction("❌ 退出桌面精灵")

        # Execute menu
        selected = menu.exec_(QCursor.pos())

        if selected == action_poke or selected == action_cheer:
            self.trigger_cheer()
        elif selected == act_b_sunshine:
            self.set_style(self.STYLE_BOY_SUNSHINE)
        elif selected == act_b_hawaiian:
            self.set_style(self.STYLE_BOY_HAWAIIAN)
        elif selected == act_g_chibi:
            self.set_style(self.STYLE_GIRL_CHIBI)
        elif selected == act_g_card:
            self.set_style(self.STYLE_GIRL_CARD)
        elif selected == act_b_card1:
            self.set_style(self.STYLE_BOY_HAWAIIAN_CARD)
        elif selected == act_b_card2:
            self.set_style(self.STYLE_BOY_SUNSHINE_CARD)
        elif selected == action_next_style:
            self.next_style()
        elif selected == action_toggle_bubbles:
            self.enable_bubbles = not self.enable_bubbles
        elif selected == action_size_s:
            self.set_character_width(160)
        elif selected == action_size_m:
            self.set_character_width(220)
        elif selected == action_size_l:
            self.set_character_width(280)
        elif selected == action_size_xl:
            self.set_character_width(340)
        elif selected == action_pomodoro:
            if self.companion.is_pomodoro_active():
                self.companion.cancel_pomodoro()
                self.dialog.show_message("番茄钟已取消，随时可以重新开启哦~", category="cheer")
            else:
                self.start_pomodoro()
        elif selected == action_toggle_top:
            self.toggle_always_on_top()
        elif selected == action_quit:
            self.close_pet()

    def set_style(self, style_name):
        """Set active character style and adapt window geometry to natural aspect ratio."""
        if style_name in self.ALL_STYLES:
            self.current_style = style_name
            self.update_geometry_size()
            self.update()
            self.trigger_cheer()

    def next_style(self):
        """Cycle to the next character style."""
        idx = self.ALL_STYLES.index(self.current_style)
        next_idx = (idx + 1) % len(self.ALL_STYLES)
        self.set_style(self.ALL_STYLES[next_idx])

    def set_character_width(self, width):
        self.target_width = width
        self.update_geometry_size()

    def start_pomodoro(self):
        self.companion.start_pomodoro(25)

    def toggle_always_on_top(self):
        is_top = bool(self.windowFlags() & Qt.WindowStaysOnTopHint)
        if is_top:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()

    def close_pet(self):
        self.dialog.close()
        self.close()
