# pipe_table_widget.py

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QDoubleSpinBox, QSpinBox, QComboBox
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
        suction_input_box = QWidget()
        middle_box = QWidget()
        discharge_input_box = QWidget()

        
        suction_input_box_layout = QVBoxLayout()
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
        
        self.quantity_suction = []
        self.quantity_discharge = []

        # Size of the line
        ## suction
        suction_size_layout = QHBoxLayout()
        suction_size_layout.addWidget(QLabel("Bitola"))

        self.input_size_list_suction = QComboBox()
        self.input_size_list_suction.addItems([
                "13 (1/2\")",
                "19 (3/4\")",
                "25 (1\")",
                "32 (1.1/4\")",
                "38 (1.1/2\")",
                "50 (2\")",
                "63 (2.1/2\")",
                "75 (3\")",
                "100 (4\")",
                "125 (5\")",
                "150 (6\")",
                "200 (8\")",
                "250 (10\")",
                "300 (12\")",
                "350 (14\")",
                ])
        
        suction_size_layout.addWidget(self.input_size_list_suction)
        suction_input_box_layout.addLayout(suction_size_layout)

        ## discharge
        discharge_size_layout = QHBoxLayout()
        discharge_size_layout.addWidget(QLabel("Bitola"))

        self.input_size_list_discharge = QComboBox()
        self.input_size_list_discharge.addItems([
                "13 (1/2\")",
                "19 (3/4\")",
                "25 (1\")",
                "32 (1.1/4\")",
                "38 (1.1/2\")",
                "50 (2\")",
                "63 (2.1/2\")",
                "75 (3\")",
                "100 (4\")",
                "125 (5\")",
                "150 (6\")",
                "200 (8\")",
                "250 (10\")",
                "300 (12\")",
                "350 (14\")",
                ])
        
        discharge_size_layout.addWidget(self.input_size_list_discharge)
        discharge_input_box_layout.addLayout(discharge_size_layout)


        # Headers
        input_header = QHBoxLayout()
        input_header.addWidget(QLabel("Descrição"))
        input_header.addWidget(QLabel("Quantidade"))

        suction_input_box_layout.addLayout(input_header)

        input_header2 = QHBoxLayout()
        input_header2.addWidget(QLabel("Descrição"))
        input_header2.addWidget(QLabel("Quantidade"))
        discharge_input_box_layout.addLayout(input_header2)

        # Loop que cria o layout da entrada do input da sucção
        for label, value in zip(input_labels, input_values):
            # Horizontal layout for each pair
            h_layout = QHBoxLayout()

            # Create QLabel
            input_label = QLabel(label)
            input_label.setMinimumWidth(100)


            # Create QSpinBox
            input_spin_box = QDoubleSpinBox()
            input_spin_box.setValue(value)
            input_spin_box.setDecimals(0)
            if label == "Trecho Retilineo":
                input_spin_box.setDecimals(2)
                input_spin_box.setSingleStep(0.1)

            # Adicionar uma referência ao input_spin_box
            self.quantity_suction.append(input_spin_box)

            # Adicionar os widgets no layout horizontal
            h_layout.addWidget(input_label)

            h_layout.addWidget(input_spin_box)

            suction_input_box_layout.addLayout(h_layout)

        # Loop que cria o layout da entrada do input da sucção
        for label, value in zip(input_labels, input_values):
            # Horizontal layout for each pair
            h_layout = QHBoxLayout()

            # Create QLabel
            input_label = QLabel(label)
            input_label.setMinimumWidth(100)


            # Create QSpinBox
            input_spin_box = QDoubleSpinBox()
            input_spin_box.setValue(value)
            input_spin_box.setDecimals(0)
            if label == "Trecho Retilineo":
                input_spin_box.setDecimals(2)
                input_spin_box.setSingleStep(0.1)

            # Adicionar uma referência ao input_spin_box
            self.quantity_discharge.append(input_spin_box)

            # Adicionar os widgets no layout horizontal
            h_layout.addWidget(input_label)
            h_layout.addWidget(input_spin_box)

            discharge_input_box_layout.addLayout(h_layout)
        # Widget Central com a Imagem Explicatoria
    
        diagram_image_label = QLabel()
        diagram_image_pixmap = QPixmap('src\/UI\/img\/diagram-image.png')
        diagram_image_label.setPixmap(diagram_image_pixmap)
        middle_box_layout = QHBoxLayout()
        middle_box_layout.addWidget(diagram_image_label)
        middle_box.setLayout(middle_box_layout)
        
        ## Colocar o widget no main Widget
        suction_input_box.setLayout(suction_input_box_layout)
        discharge_input_box.setLayout(discharge_input_box_layout)

        ##
        suction_input_box.setMaximumWidth(320)
        suction_input_box.setMinimumWidth(300)
        discharge_input_box.setMaximumWidth(320)
        discharge_input_box.setMinimumWidth(300)

        ## Set up main windows
        main_layout = QHBoxLayout()
        main_layout.addWidget(suction_input_box)
        main_layout.addStretch()
        main_layout.addWidget(middle_box)
        main_layout.addStretch()
        main_layout.addWidget(discharge_input_box)
        
        self.setLayout(main_layout)

    

    def get_input_data():
        None

    def get_spinbox_values_suction(self):
        return [spin_box.value() for spin_box in self.quantity_suction]

    def get_spinbox_values_discharge(self):
        return [spin_box.value() for spin_box in self.quantity_discharge]