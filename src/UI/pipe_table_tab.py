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

        ####
        sucction_pipe_length_box_label = QLabel("Trecho Retilíneo")
        self.sucction_pipe_length_box_value = QDoubleSpinBox()
        self.sucction_pipe_length_box_value.setMaximumWidth(100)
        self.sucction_pipe_length_box_value.setDecimals(2)
        self.sucction_pipe_length_box_value.setValue(54.20)
        sucction_pipe_length_box_layout = QHBoxLayout()
        sucction_pipe_length_box_layout.addWidget(sucction_pipe_length_box_label)
        sucction_pipe_length_box_layout.addWidget(self.sucction_pipe_length_box_value)

        sucction_input_box_layout.addLayout(sucction_pipe_length_box_layout)

        ####
        sucction_height_dif_box_label = QLabel("Diferença de Altura")
        self.sucction_height_dif_box_value = QSpinBox()
        self.sucction_height_dif_box_value.setMaximumWidth(100)
        self.sucction_height_dif_box_value.setValue(2)
        sucction_height_dif_box_layout = QHBoxLayout()
        sucction_height_dif_box_layout.addWidget(sucction_height_dif_box_label)
        sucction_height_dif_box_layout.addWidget(self.sucction_height_dif_box_value)

        sucction_input_box_layout.addLayout(sucction_height_dif_box_layout)

        ####
        sucction_elbow_90_lr_box_label = QLabel("Cotovelo 90° Raio Longo")
        self.sucction_elbow_90_lr_box_value = QSpinBox()
        self.sucction_elbow_90_lr_box_value.setMaximumWidth(100)
        sucction_elbow_90_lr_box_layout = QHBoxLayout()
        sucction_elbow_90_lr_box_layout.addWidget(sucction_elbow_90_lr_box_label)
        sucction_elbow_90_lr_box_layout.addWidget(self.sucction_elbow_90_lr_box_value)

        sucction_input_box_layout.addLayout(sucction_elbow_90_lr_box_layout)

        ####
        sucction_elbow_90_mr_box_label = QLabel("Cotovelo 90° Raio Medio")
        self.sucction_elbow_90_mr_box_value = QSpinBox()
        self.sucction_elbow_90_mr_box_value.setMaximumWidth(100)
        sucction_elbow_90_mr_box_layout = QHBoxLayout()
        sucction_elbow_90_mr_box_layout.addWidget(sucction_elbow_90_mr_box_label)
        sucction_elbow_90_mr_box_layout.addWidget(self.sucction_elbow_90_mr_box_value)

        sucction_input_box_layout.addLayout(sucction_elbow_90_mr_box_layout)

        ####
        sucction_elbow_90_sr_box_label = QLabel("Cotovelo 90° Raio Curto")
        self.sucction_elbow_90_sr_box_value = QSpinBox()
        self.sucction_elbow_90_sr_box_value.setMaximumWidth(100)
        sucction_elbow_90_sr_box_layout = QHBoxLayout()
        sucction_elbow_90_sr_box_layout.addWidget(sucction_elbow_90_sr_box_label)
        sucction_elbow_90_sr_box_layout.addWidget(self.sucction_elbow_90_sr_box_value)

        sucction_input_box_layout.addLayout(sucction_elbow_90_sr_box_layout)

        ####
        sucction_elbow_45_box_label = QLabel("Cotovelo 45°")
        self.sucction_elbow_45_box_value = QSpinBox()
        self.sucction_elbow_45_box_value.setMaximumWidth(100)
        sucction_elbow_45_box_layout = QHBoxLayout()
        sucction_elbow_45_box_layout.addWidget(sucction_elbow_45_box_label)
        sucction_elbow_45_box_layout.addWidget(self.sucction_elbow_45_box_value)

        sucction_input_box_layout.addLayout(sucction_elbow_45_box_layout)

        ####
        sucction_curve_90_rl_box_label = QLabel("Curva 90° Raio Longo")
        self.sucction_curve_90_rl_box_value = QSpinBox()
        self.sucction_curve_90_rl_box_value.setMaximumWidth(100)
        sucction_curve_90_rl_box_layout = QHBoxLayout()
        sucction_curve_90_rl_box_layout.addWidget(sucction_curve_90_rl_box_label)
        sucction_curve_90_rl_box_layout.addWidget(self.sucction_curve_90_rl_box_value)

        sucction_input_box_layout.addLayout(sucction_curve_90_rl_box_layout)
        
        ####
        sucction_curve_90_sr_box_label = QLabel("Curva 90° Raio Curto")
        self.sucction_curve_90_sr_box_value = QSpinBox()
        self.sucction_curve_90_sr_box_value.setMaximumWidth(100)
        sucction_curve_90_sr_box_layout = QHBoxLayout()
        sucction_curve_90_sr_box_layout.addWidget(sucction_curve_90_sr_box_label)
        sucction_curve_90_sr_box_layout.addWidget(self.sucction_curve_90_sr_box_value)

        sucction_input_box_layout.addLayout(sucction_curve_90_sr_box_layout)

        ####
        sucction_curve_45_label = QLabel("Curva 45°")
        self.sucction_curve_45_value = QSpinBox()
        self.sucction_curve_45_value.setMaximumWidth(100)
        sucction_curve_45_layout = QHBoxLayout()
        sucction_curve_45_layout.addWidget(sucction_curve_45_label)
        sucction_curve_45_layout.addWidget(self.sucction_curve_45_value)

        sucction_input_box_layout.addLayout(sucction_curve_45_layout)

        ####
        sucction_norm_entr_label = QLabel("Entrada Arredondada")
        self.sucction_norm_entr_value = QSpinBox()
        self.sucction_norm_entr_value.setMaximumWidth(100)
        sucction_norm_entr_layout = QHBoxLayout()
        sucction_norm_entr_layout.addWidget(sucction_norm_entr_label)
        sucction_norm_entr_layout.addWidget(self.sucction_norm_entr_value)

        sucction_input_box_layout.addLayout(sucction_norm_entr_layout)

        ####
        sucction_entr_bord_label = QLabel("Entrada de Borda")
        self.sucction_entr_bord_value = QSpinBox()
        self.sucction_entr_bord_value.setMaximumWidth(100)
        sucction_entr_bord_layout = QHBoxLayout()
        sucction_entr_bord_layout.addWidget(sucction_entr_bord_label)
        sucction_entr_bord_layout.addWidget(self.sucction_entr_bord_value)

        sucction_input_box_layout.addLayout(sucction_entr_bord_layout)

        ####
        sucction_gate_valve_open_box_label = QLabel("Válvula Gaveta Aberta")
        self.sucction_gate_valve_open_box_value = QSpinBox()
        self.sucction_gate_valve_open_box_value.setMaximumWidth(100)
        sucction_gate_valve_open_box_layout = QHBoxLayout()
        sucction_gate_valve_open_box_layout.addWidget(sucction_gate_valve_open_box_label)
        sucction_gate_valve_open_box_layout.addWidget(self.sucction_gate_valve_open_box_value)

        sucction_input_box_layout.addLayout(sucction_gate_valve_open_box_layout)

        ####
        sucction_curve_90_sr_box_label = QLabel("Válvula Angular Aberta")
        self.sucction_curve_90_sr_box_value = QSpinBox()
        self.sucction_curve_90_sr_box_value.setMaximumWidth(100)
        sucction_curve_90_sr_box_layout = QHBoxLayout()
        sucction_curve_90_sr_box_layout.addWidget(sucction_curve_90_sr_box_label)
        sucction_curve_90_sr_box_layout.addWidget(self.sucction_curve_90_sr_box_value)

        sucction_input_box_layout.addLayout(sucction_curve_90_sr_box_layout)


        ##------------------------------------------##

        ####
        discharge_pipe_length_box_label = QLabel("Trecho Retilíneo")
        self.discharge_pipe_length_box_value = QDoubleSpinBox()
        self.discharge_pipe_length_box_value.setMaximumWidth(100)
        self.discharge_pipe_length_box_value.setDecimals(2)
        self.discharge_pipe_length_box_value.setValue(54.20)
        discharge_pipe_length_box_layout = QHBoxLayout()
        discharge_pipe_length_box_layout.addWidget(discharge_pipe_length_box_label)
        discharge_pipe_length_box_layout.addWidget(self.discharge_pipe_length_box_value)

        
        discharge_input_box_layout.addLayout(discharge_pipe_length_box_layout)

        ####
        discharge_height_dif_box_label = QLabel("Diferença de Altura")
        self.discharge_height_dif_box_value = QSpinBox()
        self.discharge_height_dif_box_value.setMaximumWidth(100)
        discharge_height_dif_box_layout = QHBoxLayout()
        discharge_height_dif_box_layout.addWidget(discharge_height_dif_box_label)
        discharge_height_dif_box_layout.addWidget(self.discharge_height_dif_box_value)

        discharge_input_box_layout.addLayout(discharge_height_dif_box_layout)

        ####
        discharge_elbow_90_lr_box_label = QLabel("Cotovelo 90° Raio Longo")
        self.discharge_elbow_90_lr_box_value = QSpinBox()
        self.discharge_elbow_90_lr_box_value.setMaximumWidth(100)
        discharge_elbow_90_lr_box_layout = QHBoxLayout()
        discharge_elbow_90_lr_box_layout.addWidget(discharge_elbow_90_lr_box_label)
        discharge_elbow_90_lr_box_layout.addWidget(self.discharge_elbow_90_lr_box_value)

        discharge_input_box_layout.addLayout(discharge_elbow_90_lr_box_layout)

        ####
        discharge_elbow_90_mr_box_label = QLabel("Cotovelo 90° Raio Medio")
        self.discharge_elbow_90_mr_box_value = QSpinBox()
        self.discharge_elbow_90_mr_box_value.setMaximumWidth(100)
        discharge_elbow_90_mr_box_layout = QHBoxLayout()
        discharge_elbow_90_mr_box_layout.addWidget(discharge_elbow_90_mr_box_label)
        discharge_elbow_90_mr_box_layout.addWidget(self.discharge_elbow_90_mr_box_value)

        discharge_input_box_layout.addLayout(discharge_elbow_90_mr_box_layout)

        ####
        discharge_elbow_90_sr_box_label = QLabel("Cotovelo 90° Raio Curto")
        self.discharge_elbow_90_sr_box_value = QSpinBox()
        self.discharge_elbow_90_sr_box_value.setMaximumWidth(100)
        discharge_elbow_90_sr_box_layout = QHBoxLayout()
        discharge_elbow_90_sr_box_layout.addWidget(discharge_elbow_90_sr_box_label)
        discharge_elbow_90_sr_box_layout.addWidget(self.discharge_elbow_90_sr_box_value)

        discharge_input_box_layout.addLayout(discharge_elbow_90_sr_box_layout)

        ####
        discharge_elbow_45_box_label = QLabel("Cotovelo 45°")
        self.discharge_elbow_45_box_value = QSpinBox()
        self.discharge_elbow_45_box_value.setMaximumWidth(100)
        discharge_elbow_45_box_layout = QHBoxLayout()
        discharge_elbow_45_box_layout.addWidget(discharge_elbow_45_box_label)
        discharge_elbow_45_box_layout.addWidget(self.discharge_elbow_45_box_value)

        discharge_input_box_layout.addLayout(discharge_elbow_45_box_layout)

        ####
        discharge_curve_90_rl_box_label = QLabel("Curva 90° Raio Longo")
        self.discharge_curve_90_rl_box_value = QSpinBox()
        self.discharge_curve_90_rl_box_value.setMaximumWidth(100)
        discharge_curve_90_rl_box_layout = QHBoxLayout()
        discharge_curve_90_rl_box_layout.addWidget(discharge_curve_90_rl_box_label)
        discharge_curve_90_rl_box_layout.addWidget(self.discharge_curve_90_rl_box_value)

        discharge_input_box_layout.addLayout(discharge_curve_90_rl_box_layout)
        
        ####
        discharge_curve_90_sr_box_label = QLabel("Curva 90° Raio Curto")
        self.discharge_curve_90_sr_box_value = QSpinBox()
        self.discharge_curve_90_sr_box_value.setMaximumWidth(100)
        discharge_curve_90_sr_box_layout = QHBoxLayout()
        discharge_curve_90_sr_box_layout.addWidget(discharge_curve_90_sr_box_label)
        discharge_curve_90_sr_box_layout.addWidget(self.discharge_curve_90_sr_box_value)

        discharge_input_box_layout.addLayout(discharge_curve_90_sr_box_layout)


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
        sucction_input_box.setMaximumWidth(300)
        sucction_input_box.setMinimumWidth(250)
        discharge_input_box.setMaximumWidth(300)
        discharge_input_box.setMinimumWidth(250)

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