# pipe_table_widget.py

from PyQt6.QtWidgets import QWidget, QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QDoubleSpinBox, QSpinBox
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap

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

        
        sucction_input_box_layout = QVBoxLayout()
        discharge_input_box_layout = QVBoxLayout()
        # Aqui eu preciso adicionar um QWidget com Layout Horizontal com um QLabel e um QText para cada tipo de perda de carga localizada

        # Nomes de cada componente do input
        input_labels = ["Trecho Retilineo", "Diferença de Altura", "Cotovelo 90° Raio Longo", "Cotovelo 90° Raio Médio", "Cotovelo 90° Raio Curto",
        "Cotovelo 45°", "Curva 90° Raio Longo", "Curva 90° Raio Curto", "Curva 45°", "Entrada Normal", "Entrada de Borda",
        "Válvula Gaveta Aberta", "Válvula Globo Aberta", "Válvula Ângular Aberta", "Passagem Reta Tê",
        "Derivação Tê", "Bifurcação Tê", "Válvula de Pé e Crivo", "Saída de Canalização",
        "Válvula de Retenção Leve", "Válvula de Retenção Pesado"] # Dados de Entrada
        
        # Criar o valor inicial de cada input para testes
        input_values = [0 for element in range(21)] # mesmo tamamho do input_labels
        
        self.spin_boxes_sucction = []
        self.spin_boxes_discharge = []

        # Loop que cria o layout da entrada do input da sucção
        for label, value in zip(input_labels, input_values):
            # Horizontal layout for each pair
            h_layout = QHBoxLayout()

            # Create QLabel
            label = QLabel(label)

            # Create QSpinBox
            spin_box = QDoubleSpinBox()
            spin_box.setValue(value)
            spin_box.setDecimals(0)
            if label == "Trecho Retilineo":
                spin_box.setDecimals(2)

            # Adicionar uma referência ao spin_box
            self.spin_boxes_sucction.append(spin_box)

            # Adicionar os widgets no layout horizontal
            h_layout.addWidget(label)
            h_layout.addWidget(spin_box)

            sucction_input_box_layout.addLayout(h_layout)

        # Loop que cria o layout da entrada do input da sucção
        for label, value in zip(input_labels, input_values):
            # Horizontal layout for each pair
            h_layout = QHBoxLayout()

            # Create QLabel
            label = QLabel(label)

            # Create QSpinBox
            spin_box = QDoubleSpinBox()
            spin_box.setDecimals(0)
            if label == "Trecho Retilineo":
                spin_box.setDecimals(2)
            spin_box.setValue(value)
            # Adicionar uma referência ao spin_box
            self.spin_boxes_discharge.append(spin_box)

            # Adicionar os widgets no layout horizontal
            h_layout.addWidget(label)
            h_layout.addWidget(spin_box)

            discharge_input_box_layout.addLayout(h_layout)


        # Widget Central com a Imagem Explicatoria
    
        diagram_image_label = QLabel()
        diagram_image_pixmap = QPixmap('src\/UI\/img\/diagram-image.png')
        diagram_image_label.setPixmap(diagram_image_pixmap)
        middle_box_layout = QHBoxLayout()
        middle_box_layout.addWidget(diagram_image_label)
        middle_box.setLayout(middle_box_layout)
        
        ## Colocar o widget no main Widget
        sucction_input_box.setLayout(sucction_input_box_layout)
        discharge_input_box.setLayout(discharge_input_box_layout)

        ##
        sucction_input_box.setMaximumWidth(320)
        sucction_input_box.setMinimumWidth(300)
        discharge_input_box.setMaximumWidth(320)
        discharge_input_box.setMinimumWidth(300)

        ## Set up main windows
        main_layout = QHBoxLayout()
        main_layout.addWidget(sucction_input_box)
        main_layout.addStretch()
        main_layout.addWidget(middle_box)
        main_layout.addStretch()
        main_layout.addWidget(discharge_input_box)
        
        self.setLayout(main_layout)

    

    def get_input_data():
        None

    def get_spinbox_values_sucction(self):
        return [spin_box.value() for spin_box in self.spin_boxes_sucction]

    def get_spinbox_values_discharge(self):
        return [spin_box.value() for spin_box in self.spin_boxes_discharge]