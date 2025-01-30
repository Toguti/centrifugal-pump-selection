import sys
import sqlite3
import json
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QMessageBox)
from UI.func.pump_db import db_path

db_path = "./src/db/pump_data.db"

class PumpSelectionWidget(QWidget):
    def __init__(self):
        super().__init__()