# pipe_table_widget.py

from PyQt6.QtWidgets import QWidget, QGroupBox, QHBoxLayout
from PyQt6.QtCore import Qt
from UI.data.input_variables import *
import pandas as pd


class FluidPropInput(QWidget):
    def __init__(self):
        super().__init__()

        '''
         Preciso criar 3 grupos na horizontal, o primeiro será o input antes da bomba, 
         o do meio uma imagem representando o sistema, e o ultimo grupo será o input após a bomba.
        '''
        

        sucction_input = QGroupBox("Dados de entrada sucção")

        # Criação dos box para cada seguimento
        sucction_input_box = QGroupBox("Dados de Entrada da Sucção")
        middle_box = QGroupBox("Esquema")
        discharge_input_box = QGroupBox("Dados de Entrada do Recalque")

        
        # Aqui eu preciso adicionar um QWidget com Layout Horizontal com um QLabel e um QText para cada tipo de perda de carga localizada

        for i in header_second_line:
            print(i)

        
