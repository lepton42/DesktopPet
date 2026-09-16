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

    MODE_CHIBI = "chibi"
    MODE_PHOTO = "photo"

    STATE_IDLE = "idle"
    STATE_CHEER = "cheer"

    def __init__(self, assets_dir):
        super().__init__()
        self.assets_dir = assets_dir

        # Window properties: Frameless, transparent background, always on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)

        # Pet states & appearance
        self.current_mode = self.MODE_CHIBI
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
        """Load pixmaps for chibi and photo modes."""
        idle_path = os.path.join(self.assets_dir, "pet_idle.png")
        cheer_path = os.path.join(self.assets_dir, "pet_cheer.png")
        photo_path = os.path.join(self.assets_dir, "pet_photo_card.png")
        bubble_path = os.path.join(self.assets_dir, "bubble.png")

        if os.path.exists(idle_path):
            self.pixmaps["chibi_idle"] = QPixmap(idle_path)
        if os.path.exists(cheer_path):
            self.pixmaps["chibi_cheer"] = QPixmap(cheer_path)
        if os.path.exists(photo_path):
            self.pixmaps["photo_card"] = QPixmap(photo_path)
        if os.path.exists(bubble_path):
            self.pixmaps["bubble"] = QPixmap(bubble_path)

    def init_bubbles(self):
        """Create floating bubble particles."""
        self.bubbles.clear()
        w, h = self.width(), self.height()
        count = 14
        for _ in range(count):
            self.bubbles.append(BubbleParticle(w, h))

    def update_geometry_size(self):
        """Recalculate window dimensions based on target character width."""
        char_w = self.target_width
        char_h = int(char_w * 1.4)

        # Give extra side and vertical margin for floating bubbles
        margin_x = 70
        margin_y = 60

        total_w = char_w + margin_x * 2
        total_h = char_h + margin_y * 2
        self.char_rect = QRectF(margin_x, margin_y, char_w, char_h)
        self.resize(total_w, total_h)

        # Update bubble boundary constraints
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
        """Trigger cheerful toast reaction."""
        self.current_state = self.STATE_CHEER
        self.bounce_offset = -18.0  # Little jump
        self.update()

        self.state_timer.stop()
        self.state_timer.start(3000)

        self.dialog.show_message(text=quote, category="cheer")

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
            self.dialog.show_message(category="cheer", duration_ms=4000)

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

        # 2. Select Sprite Pixmap
        active_pix = None
        if self.current_mode == self.MODE_PHOTO:
            active_pix = self.pixmaps.get("photo_card")
        else:
            if self.current_state == self.STATE_CHEER:
                active_pix = self.pixmaps.get("chibi_cheer") or self.pixmaps.get("chibi_idle")
            else:
                active_pix = self.pixmaps.get("chibi_idle")

        if active_pix:
            # Calculate floating hover offset
            hover_y = math.sin(self.float_phase) * 5.0 + self.bounce_offset
            draw_rect = QRectF(
                self.char_rect.x(),
                self.char_rect.y() + hover_y,
                self.char_rect.width(),
                self.char_rect.height()
            )

            # Draw subtle ground shadow beneath the floating pet
            shadow_w = self.char_rect.width() * 0.6
            shadow_h = 14
            shadow_x = self.char_rect.x() + (self.char_rect.width() - shadow_w) / 2
            shadow_y = self.char_rect.y() + self.char_rect.height() - 6
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(0, 0, 0, 32)))
            painter.drawEllipse(QRectF(shadow_x, shadow_y, shadow_w, shadow_h))

            # Draw pet sprite
            painter.drawPixmap(draw_rect.toRect(), active_pix)

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
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid rgba(255, 180, 200, 0.6);
                border-radius: 10px;
                padding: 6px;
                font-family: 'PingFang SC', sans-serif;
                font-size: 13px;
                color: #333333;
            }
            QMenu::item {
                padding: 6px 20px;
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
        action_cheer = menu.addAction("🥂 举杯干杯 (Cheers!)")
        menu.addSeparator()

        # Appearance Switch
        mode_text = "🎨 切换为【唯美照片立绘】" if self.current_mode == self.MODE_CHIBI else "🎨 切换为【Q版萌系精灵】"
        action_switch_mode = menu.addAction(mode_text)

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
        elif selected == action_switch_mode:
            self.toggle_mode()
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

    def toggle_mode(self):
        if self.current_mode == self.MODE_CHIBI:
            self.current_mode = self.MODE_PHOTO
        else:
            self.current_mode = self.MODE_CHIBI
        self.update()

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
