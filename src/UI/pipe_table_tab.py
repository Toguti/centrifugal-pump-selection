# pipe_table_widget.py

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QLabel, QSpinBox, QDoubleSpinBox
from PyQt6.QtCore import Qt
from UI.data.header_table_data import *
import pandas as pd

class FluidPropInput(QWidget):
    def __init__(self):
        super().__init__()