# pipe_table_widget.py

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QDoubleSpinBox, QSpinBox, QComboBox, QGroupBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from UI.data.input_variables import *
import pandas as pd


class SystemInputWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Inicializa as listas de spinboxes antes de usar
        self.quantity_suction = []
        self.quantity_discharge = []

        # Cria os widgets principais
        suction_group = self._create_group_box("Sucção")
        middle_box = self._create_middle_box()
        discharge_group = self._create_group_box("Recalque")

        # Configura layout dos inputs
        self._setup_input_layout(suction_group, is_suction=True)
        self._setup_input_layout(discharge_group, is_suction=False)

        # Removendo restrições fixas de largura para permitir que 
        # o layout com proporções funcione corretamente

        # Configura layout principal com proporções 3:6:3 (total 12 partes)
        main_layout = QHBoxLayout()
        main_layout.addWidget(suction_group, 3)
        main_layout.addWidget(middle_box, 6)
        main_layout.addWidget(discharge_group, 3)
        
        self.setLayout(main_layout)

    def _create_group_box(self, title):
        """Cria um QGroupBox com o título especificado"""
        group_box = QGroupBox(title)
        return group_box

    def _create_middle_box(self):
        """Cria o widget central com a imagem explicativa"""
        middle_box = QWidget()
        diagram_image_label = QLabel()
        diagram_image_pixmap = QPixmap('src/UI/img/diagram-image.png')
        diagram_image_label.setPixmap(diagram_image_pixmap)
        diagram_image_label.setScaledContents(True)  # Imagem se ajusta ao container
        
        middle_box_layout = QVBoxLayout()
        middle_box_layout.addWidget(diagram_image_label)
        middle_box_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centraliza a imagem
        middle_box.setLayout(middle_box_layout)
        
        return middle_box

    def _setup_input_layout(self, group_box, is_suction=True):
        """Configura o layout de entrada para sucção ou recalque"""
        # Nomes de cada componente do input
        input_labels = [
            "Trecho Retilineo", "Diferença de Altura", 
            "Cotovelo 90° Raio Longo", "Cotovelo 90° Raio Médio", "Cotovelo 90° Raio Curto",
            "Cotovelo 45°", "Curva 90° Raio Longo", "Curva 90° Raio Curto", "Curva 45°", 
            "Entrada Normal", "Entrada de Borda", "Válvula Gaveta Aberta", 
            "Válvula Globo Aberta", "Válvula Ângular Aberta", "Passagem Reta Tê",
            "Derivação Tê", "Bifurcação Tê", "Válvula de Pé e Crivo", 
            "Saída de Canalização", "Válvula de Retenção Leve", "Válvula de Retenção Pesado"
        ]
        
        # Valores iniciais para testes
        input_values_suction = {
            "Trecho Retilineo": 6, "Diferença de Altura": 2, 
            "Cotovelo 90° Raio Longo": 0, "Cotovelo 90° Raio Médio": 0, "Cotovelo 90° Raio Curto": 0,
            "Cotovelo 45°": 0, "Curva 90° Raio Longo": 5, "Curva 90° Raio Curto": 0, "Curva 45°": 4, 
            "Entrada Normal": 0, "Entrada de Borda": 1, "Válvula Gaveta Aberta": 3, 
            "Válvula Globo Aberta": 0, "Válvula Ângular Aberta": 0, "Passagem Reta Tê": 0,
            "Derivação Tê": 0, "Bifurcação Tê": 0, "Válvula de Pé e Crivo": 1, 
            "Saída de Canalização": 1, "Válvula de Retenção Leve": 0, "Válvula de Retenção Pesado": 1
        }

        input_values_discharge = {
            "Trecho Retilineo": 50, "Diferença de Altura": 8, 
            "Cotovelo 90° Raio Longo": 0, "Cotovelo 90° Raio Médio": 0, "Cotovelo 90° Raio Curto": 0,
            "Cotovelo 45°": 0, "Curva 90° Raio Longo": 5, "Curva 90° Raio Curto": 0, "Curva 45°": 4, 
            "Entrada Normal": 0, "Entrada de Borda": 1, "Válvula Gaveta Aberta": 3, 
            "Válvula Globo Aberta": 0, "Válvula Ângular Aberta": 0, "Passagem Reta Tê": 0,
            "Derivação Tê": 0, "Bifurcação Tê": 0, "Válvula de Pé e Crivo": 1, 
            "Saída de Canalização": 1, "Válvula de Retenção Leve": 0, "Válvula de Retenção Pesado": 1
        }
        
        # Seleciona os valores apropriados baseado no tipo de entrada
        input_values = input_values_suction if is_suction else input_values_discharge
        
        # As listas já foram inicializadas no __init__
            
        # Cria layout para o grupo com alinhamento ao topo
        group_layout = QVBoxLayout()
        group_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        group_layout.setSpacing(5)  # Menor espaçamento entre itens
        
        # Adiciona cabeçalho com mesma proporção dos itens (2:1)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 5)
        
        desc_label = QLabel("Descrição")
        desc_label.setFixedHeight(20)  # Altura fixa para o header
        
        quant_label = QLabel("Quantidade")
        quant_label.setFixedHeight(20)  # Altura fixa para o header
        
        header_layout.addWidget(desc_label, 2)
        header_layout.addWidget(quant_label, 1)
        group_layout.addLayout(header_layout)
        
        # Adiciona inputs
        for label in input_labels:
            h_layout = QHBoxLayout()
            
            # Cria QLabel com tamanho fixo
            input_label = QLabel(label)
            input_label.setFixedHeight(20)  # Altura fixa
            
            # Cria QSpinBox com tamanho fixo
            input_spin_box = QDoubleSpinBox()
            input_spin_box.setFixedHeight(20)  # Altura fixa para o spinbox
            input_spin_box.setValue(input_values[label])
            input_spin_box.setDecimals(0)
            
            # Configurações especiais para o trecho retilíneo
            if label == "Trecho Retilineo":
                input_spin_box.setDecimals(2)
                input_spin_box.setSingleStep(0.1)
                input_spin_box.setMaximum(99999)
                
            # Adiciona ao layout com proporções 2:1 para os campos
            h_layout.addWidget(input_label, 2)
            h_layout.addWidget(input_spin_box, 1)
            h_layout.setContentsMargins(0, 0, 0, 0)  # Remove margens extras
            group_layout.addLayout(h_layout)
            
            # Adiciona à lista apropriada
            if is_suction:
                self.quantity_suction.append(input_spin_box)
            else:
                self.quantity_discharge.append(input_spin_box)
        
        # Adiciona um stretchAtEnd para garantir que o espaço em branco fique na parte inferior
        group_layout.addStretch(1)
        
        # Define o layout do grupo
        group_box.setLayout(group_layout)

    def get_spinbox_values_suction(self):
        """Retorna os valores dos spinboxes de sucção"""
        return [spin_box.value() for spin_box in self.quantity_suction]

    def get_spinbox_values_discharge(self):
        """Retorna os valores dos spinboxes de recalque"""
        return [spin_box.value() for spin_box in self.quantity_discharge]

    def get_suction_size(self):
        """Retorna o tamanho selecionado para sucção"""
        if hasattr(self, 'input_size_list_suction'):
            return self.input_size_list_suction.currentText()
        return None

    def get_discharge_size(self):
        """Retorna o tamanho selecionado para recalque"""
        if hasattr(self, 'input_size_list_discharge'):
            return self.input_size_list_discharge.currentText()
        return None