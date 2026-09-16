# -*- coding: utf-8 -*-
"""
Desktop Pet Companion Timer & Reminders
Manages Pomodoro sessions and healthy study/work habits.
"""

from datetime import datetime
from PyQt5.QtCore import QObject, QTimer, pyqtSignal


class CompanionTimer(QObject):
    """Timer and reminder manager for the desktop pet."""

    pomodoro_tick = pyqtSignal(int)         # Remaining seconds
    pomodoro_finished = pyqtSignal()        # Session complete
    reminder_triggered = pyqtSignal(str, str) # (category, message)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Pomodoro timer (default 25 minutes = 1500 seconds)
        self.pomodoro_remaining = 0
        self.pomodoro_timer = QTimer(self)
        self.pomodoro_timer.setInterval(1000)
        self.pomodoro_timer.timeout.connect(self._on_pomodoro_tick)

        # Health reminder timer (fires every 40 minutes)
        self.health_timer = QTimer(self)
        self.health_timer.setInterval(40 * 60 * 1000)
        self.health_timer.timeout.connect(self._on_health_check)
        self.health_timer.start()

        # Late night check timer (every 15 minutes)
        self.night_timer = QTimer(self)
        self.night_timer.setInterval(15 * 60 * 1000)
        self.night_timer.timeout.connect(self._check_night_time)
        self.night_timer.start()

    def start_pomodoro(self, minutes=25):
        """Start a Pomodoro focus session."""
        self.pomodoro_remaining = minutes * 60
        self.pomodoro_timer.start()
        self.reminder_triggered.emit("pomodoro_start", "")

    def cancel_pomodoro(self):
        """Stop current Pomodoro."""
        self.pomodoro_timer.stop()
        self.pomodoro_remaining = 0

    def is_pomodoro_active(self):
        return self.pomodoro_timer.isActive()

    def _on_pomodoro_tick(self):
        if self.pomodoro_remaining > 0:
            self.pomodoro_remaining -= 1
            self.pomodoro_tick.emit(self.pomodoro_remaining)
        else:
            self.pomodoro_timer.stop()
            self.pomodoro_finished.emit()
            self.reminder_triggered.emit("pomodoro_end", "")

    def _on_health_check(self):
        """Regular stretch/water reminder."""
        if not self.is_pomodoro_active():
            self.reminder_triggered.emit("health", "")

    def _check_night_time(self):
        """Late night caring reminder."""
        now = datetime.now()
        if now.hour >= 23 or now.hour < 5:
            self.reminder_triggered.emit("night", "")
