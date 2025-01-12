from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QFontMetrics

# class RotatedLabel(QLabel):
#     def __init__(self, text="", parent=None):
#         super().__init__(text, parent)
#         self.setMinimumHeight(100)
#         self.setMinimumWidth(10)

#     def paintEvent(self, event):
#         painter = QPainter(self)
#         painter.translate(self.rect().center())
#         painter.rotate(-90)
#         painter.translate(-self.rect().center())
#         painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

class RotatedLabel(QLabel):
    def __init__(self, text, angle=-90, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.angle = angle
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.updateGeometry()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate the size of the text
        fm = QFontMetrics(self.font())
        text_rect = fm.boundingRect(self.text())
        text_width, text_height = text_rect.width(), text_rect.height()
        
        # Calculate the transformation required to rotate the text
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.angle)
        painter.translate(-text_width / 2, -text_height / 2)
        
        # Draw the text
        painter.drawText(0, 0, text_width, text_height, Qt.AlignmentFlag.AlignCenter, self.text())
        painter.end()

    def sizeHint(self):
        fm = QFontMetrics(self.font())
        text_rect = fm.boundingRect(self.text())
        return text_rect.size()

    def minimumSizeHint(self):
        return self.sizeHint()
