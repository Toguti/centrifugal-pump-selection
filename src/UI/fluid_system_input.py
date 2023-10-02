from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QGroupBox, 
    QHBoxLayout,
    QLabel,
    QLineEdit)
from PyQt6.QtCore import Qt

class fluid_system_input(QtWidgets.QGroupBox):
    def __init__ (self):
        super().__init__()

        #  Flow Rate
        flow_rate_layout = QHBoxLayout()
        flow_rate_layout.addWidget(QLabel("Target Flow Rate"))
        flow_rate_layout.addWidget(QLineEdit())
        
        # # Fluid
        # fluid_layout = QHBoxLayout()
        # flow_rate_layout.addWidget(QLabel("Target Flow Rate"))
        
        # Pipe Roughness
        pipe_roughness_layout = QHBoxLayout()
        pipe_roughness_layout.addWidget(QLabel("Roughness"))
        pipe_roughness_layout.addWidget(QLineEdit())

        # Input Widget Layout
        layout = QHBoxLayout()
        layout.addLayout(flow_rate_layout)
        layout.addLayout(pipe_roughness_layout)

        # Group Box Layout
        self.setTitle("System Input")
        self.setLayout(layout)
