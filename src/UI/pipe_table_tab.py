# pipe_table_widget.py

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QLabel, QSpinBox, QDoubleSpinBox, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator
from UI.func.rotated_label import RotatedLabel
from UI.data.header_table_data import *
import pandas as pd

class PipeTableWidget(QTableWidget):
    