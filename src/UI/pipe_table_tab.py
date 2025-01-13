# pipe_table_widget.py

from PyQt6.QtWidgets import QWidget, QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QDoubleSpinBox
from PyQt6.QtCore import Qt
from UI.data.input_variables import *
import pandas as pd


class SystemInputWidget(QWidget):
    def __init__(self):
        super().__init__()

        '''
         Preciso criar 3 grupos na horizontal, o primeiro será o input antes da bomba, 
         o do meio uma imagem representando o sistema, e o ultimo grupo será o input após a bomba.
        '''
        
        # Criação dos box para cada seguimento
        sucction_input_box = QWidget()
        middle_box = QWidget()
        discharge_input_box = QWidget()

        main_layout = QHBoxLayout()
        
        # Aqui eu preciso adicionar um QWidget com Layout Horizontal com um QLabel e um QText para cada tipo de perda de carga localizada

        pipe_length_box = QWidget()
        pipe_length_box_label = QLabel("Trecho Retilíneo")
        pipe_length_box_value = QDoubleSpinBox()
        pipe_length_box_layout = QHBoxLayout()
        pipe_length_box_layout.addWidget(pipe_length_box_label)
        pipe_length_box_layout.addWidget(pipe_length_box_value)
        pipe_length_box.setLayout(pipe_length_box_layout)

        sucction_input_box_layout = QVBoxLayout()
        sucction_input_box_layout.addWidget(pipe_length_box)
        sucction_input_box.setLayout(sucction_input_box_layout)


        main_layout.addWidget(sucction_input_box)
        
        self.setLayout(main_layout)
