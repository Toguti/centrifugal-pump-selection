# rotated_label.py

from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import Qt

class RotatedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(100)
        self.setMinimumWidth(20)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.translate(self.rect().center())
        painter.rotate(90)
        painter.translate(-self.rect().center())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

