from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

import sys

# Configure Window

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwawrgs):
        super(MainWindow, self).__init__(*args, **kwawrgs)

        #Window
        self.setWindowTitle("Janela Principal")
        self.setFixedSize(QSize(1200, 800))
        
        #Label
        label = QLabel("Texto do widget")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(label)

        #Button
        button = QPushButton("Next")
        self.setCentralWidget(button)


# Initialize Aplication

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

