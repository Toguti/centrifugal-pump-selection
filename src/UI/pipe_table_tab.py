# pipe_table_widget.py

from PyQt6.QtWidgets import QWidget, QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QDoubleSpinBox, QSpinBox
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

        
        sucction_input_box_layout = QVBoxLayout()
        discharge_input_box_layout = QVBoxLayout()
        # Aqui eu preciso adicionar um QWidget com Layout Horizontal com um QLabel e um QText para cada tipo de perda de carga localizada

        ####
        sucction_pipe_length_box = QWidget()
        sucction_pipe_length_box_label = QLabel("Trecho Retilíneo")
        sucction_pipe_length_box_value = QDoubleSpinBox()
        sucction_pipe_length_box_value.setDecimals(2)
        sucction_pipe_length_box_value.setValue(54.20)
        sucction_pipe_length_box_layout = QHBoxLayout()
        sucction_pipe_length_box_layout.addWidget(sucction_pipe_length_box_label)
        sucction_pipe_length_box_layout.addWidget(sucction_pipe_length_box_value)
        sucction_pipe_length_box.setLayout(sucction_pipe_length_box_layout)
        
        
        sucction_input_box_layout.addWidget(sucction_pipe_length_box)

        ####
        sucction_height_dif_box = QWidget()
        sucction_height_dif_box_label = QLabel("Diferença de Altura (Valor Negativo caso Afogada)")
        sucction_height_dif_box_value = QSpinBox()
        sucction_height_dif_box_layout = QHBoxLayout()
        sucction_height_dif_box_layout.addWidget(sucction_height_dif_box_label)
        sucction_height_dif_box_layout.addWidget(sucction_height_dif_box_value)
        sucction_height_dif_box.setLayout(sucction_height_dif_box_layout)

        sucction_input_box_layout.addWidget(sucction_height_dif_box)

        ####
        sucction_elbow_90_lr_box = QWidget()
        sucction_elbow_90_lr_box_label = QLabel("Cotovelo 90° Raio Longo")
        sucction_elbow_90_lr_box_value = QSpinBox()
        sucction_elbow_90_lr_box_layout = QHBoxLayout()
        sucction_elbow_90_lr_box_layout.addWidget(sucction_elbow_90_lr_box_label)
        sucction_elbow_90_lr_box_layout.addWidget(sucction_elbow_90_lr_box_value)
        sucction_elbow_90_lr_box.setLayout(sucction_elbow_90_lr_box_layout)

        sucction_input_box_layout.addWidget(sucction_elbow_90_lr_box)

        ####
        sucction_elbow_90_mr_box = QWidget()
        sucction_elbow_90_mr_box_label = QLabel("Cotovelo 90° Raio Medio")
        sucction_elbow_90_mr_box_value = QSpinBox()
        sucction_elbow_90_mr_box_layout = QHBoxLayout()
        sucction_elbow_90_mr_box_layout.addWidget(sucction_elbow_90_mr_box_label)
        sucction_elbow_90_mr_box_layout.addWidget(sucction_elbow_90_mr_box_value)
        sucction_elbow_90_mr_box.setLayout(sucction_elbow_90_mr_box_layout)

        sucction_input_box_layout.addWidget(sucction_elbow_90_mr_box)

        ####
        sucction_elbow_90_sr_box = QWidget()
        sucction_elbow_90_sr_box_label = QLabel("Cotovelo 90° Raio Curto")
        sucction_elbow_90_sr_box_value = QSpinBox()
        sucction_elbow_90_sr_box_layout = QHBoxLayout()
        sucction_elbow_90_sr_box_layout.addWidget(sucction_elbow_90_sr_box_label)
        sucction_elbow_90_sr_box_layout.addWidget(sucction_elbow_90_sr_box_value)
        sucction_elbow_90_sr_box.setLayout(sucction_elbow_90_sr_box_layout)

        sucction_input_box_layout.addWidget(sucction_elbow_90_sr_box)

        ####
        sucction_elbow_45_box = QWidget()
        sucction_elbow_45_box_label = QLabel("Cotovelo 45°")
        sucction_elbow_45_box_value = QSpinBox()
        sucction_elbow_45_box_layout = QHBoxLayout()
        sucction_elbow_45_box_layout.addWidget(sucction_elbow_45_box_label)
        sucction_elbow_45_box_layout.addWidget(sucction_elbow_45_box_value)
        sucction_elbow_45_box.setLayout(sucction_elbow_45_box_layout)

        sucction_input_box_layout.addWidget(sucction_elbow_45_box)

        ####
        sucction_curve_90_rl_box = QWidget()
        sucction_curve_90_rl_box_label = QLabel("Curva 90° Raio Longo")
        sucction_curve_90_rl_box_value = QSpinBox()
        sucction_curve_90_rl_box_layout = QHBoxLayout()
        sucction_curve_90_rl_box_layout.addWidget(sucction_curve_90_rl_box_label)
        sucction_curve_90_rl_box_layout.addWidget(sucction_curve_90_rl_box_value)
        sucction_curve_90_rl_box.setLayout(sucction_curve_90_rl_box_layout)

        sucction_input_box_layout.addWidget(sucction_curve_90_rl_box)
        
        ####
        sucction_curve_90_sr_box = QWidget()
        sucction_curve_90_sr_box_label = QLabel("Curva 90° Raio Curto")
        sucction_curve_90_sr_box_value = QSpinBox()
        sucction_curve_90_sr_box_layout = QHBoxLayout()
        sucction_curve_90_sr_box_layout.addWidget(sucction_curve_90_sr_box_label)
        sucction_curve_90_sr_box_layout.addWidget(sucction_curve_90_sr_box_value)
        sucction_curve_90_sr_box.setLayout(sucction_curve_90_sr_box_layout)

        sucction_input_box_layout.addWidget(sucction_curve_90_sr_box)



        ##------------------------------------------##

        ####
        discharge_pipe_length_box = QWidget()
        discharge_pipe_length_box_label = QLabel("Trecho Retilíneo")
        discharge_pipe_length_box_value = QDoubleSpinBox()
        discharge_pipe_length_box_value.setDecimals(2)
        discharge_pipe_length_box_value.setValue(54.20)
        discharge_pipe_length_box_layout = QHBoxLayout()
        discharge_pipe_length_box_layout.addWidget(discharge_pipe_length_box_label)
        discharge_pipe_length_box_layout.addWidget(discharge_pipe_length_box_value)
        discharge_pipe_length_box.setLayout(discharge_pipe_length_box_layout)

        
        discharge_input_box_layout.addWidget(discharge_pipe_length_box)

        ####
        discharge_height_dif_box = QWidget()
        discharge_height_dif_box_label = QLabel("Diferença de Altura (Valor Negativo caso Afogada)")
        discharge_height_dif_box_value = QSpinBox()
        discharge_height_dif_box_layout = QHBoxLayout()
        discharge_height_dif_box_layout.addWidget(discharge_height_dif_box_label)
        discharge_height_dif_box_layout.addWidget(discharge_height_dif_box_value)
        discharge_height_dif_box.setLayout(discharge_height_dif_box_layout)

        discharge_input_box_layout.addWidget(discharge_height_dif_box)

        ####
        discharge_elbow_90_lr_box = QWidget()
        discharge_elbow_90_lr_box_label = QLabel("Cotovelo 90° Raio Longo")
        discharge_elbow_90_lr_box_value = QSpinBox()
        discharge_elbow_90_lr_box_layout = QHBoxLayout()
        discharge_elbow_90_lr_box_layout.addWidget(discharge_elbow_90_lr_box_label)
        discharge_elbow_90_lr_box_layout.addWidget(discharge_elbow_90_lr_box_value)
        discharge_elbow_90_lr_box.setLayout(discharge_elbow_90_lr_box_layout)

        discharge_input_box_layout.addWidget(discharge_elbow_90_lr_box)

        ####
        discharge_elbow_90_mr_box = QWidget()
        discharge_elbow_90_mr_box_label = QLabel("Cotovelo 90° Raio Medio")
        discharge_elbow_90_mr_box_value = QSpinBox()
        discharge_elbow_90_mr_box_layout = QHBoxLayout()
        discharge_elbow_90_mr_box_layout.addWidget(discharge_elbow_90_mr_box_label)
        discharge_elbow_90_mr_box_layout.addWidget(discharge_elbow_90_mr_box_value)
        discharge_elbow_90_mr_box.setLayout(discharge_elbow_90_mr_box_layout)

        discharge_input_box_layout.addWidget(discharge_elbow_90_mr_box)

        ####
        discharge_elbow_90_sr_box = QWidget()
        discharge_elbow_90_sr_box_label = QLabel("Cotovelo 90° Raio Curto")
        discharge_elbow_90_sr_box_value = QSpinBox()
        discharge_elbow_90_sr_box_layout = QHBoxLayout()
        discharge_elbow_90_sr_box_layout.addWidget(discharge_elbow_90_sr_box_label)
        discharge_elbow_90_sr_box_layout.addWidget(discharge_elbow_90_sr_box_value)
        discharge_elbow_90_sr_box.setLayout(discharge_elbow_90_sr_box_layout)

        discharge_input_box_layout.addWidget(discharge_elbow_90_sr_box)

        ####
        discharge_elbow_45_box = QWidget()
        discharge_elbow_45_box_label = QLabel("Cotovelo 45°")
        discharge_elbow_45_box_value = QSpinBox()
        discharge_elbow_45_box_layout = QHBoxLayout()
        discharge_elbow_45_box_layout.addWidget(discharge_elbow_45_box_label)
        discharge_elbow_45_box_layout.addWidget(discharge_elbow_45_box_value)
        discharge_elbow_45_box.setLayout(discharge_elbow_45_box_layout)

        discharge_input_box_layout.addWidget(discharge_elbow_45_box)

        ####
        discharge_curve_90_rl_box = QWidget()
        discharge_curve_90_rl_box_label = QLabel("Curva 90° Raio Longo")
        discharge_curve_90_rl_box_value = QSpinBox()
        discharge_curve_90_rl_box_layout = QHBoxLayout()
        discharge_curve_90_rl_box_layout.addWidget(discharge_curve_90_rl_box_label)
        discharge_curve_90_rl_box_layout.addWidget(discharge_curve_90_rl_box_value)
        discharge_curve_90_rl_box.setLayout(discharge_curve_90_rl_box_layout)

        discharge_input_box_layout.addWidget(discharge_curve_90_rl_box)
        
        ####
        discharge_curve_90_sr_box = QWidget()
        discharge_curve_90_sr_box_label = QLabel("Curva 90° Raio Curto")
        discharge_curve_90_sr_box_value = QSpinBox()
        discharge_curve_90_sr_box_layout = QHBoxLayout()
        discharge_curve_90_sr_box_layout.addWidget(discharge_curve_90_sr_box_label)
        discharge_curve_90_sr_box_layout.addWidget(discharge_curve_90_sr_box_value)
        discharge_curve_90_sr_box.setLayout(discharge_curve_90_sr_box_layout)

        discharge_input_box_layout.addWidget(discharge_curve_90_sr_box)



        ## Colocar o widget no main Widget
        sucction_input_box.setLayout(sucction_input_box_layout)
        discharge_input_box.setLayout(discharge_input_box_layout)

        ## Set up main windows
        main_layout = QHBoxLayout()
        main_layout.addWidget(sucction_input_box)
        main_layout.addWidget(discharge_input_box)
        
        self.setLayout(main_layout)

    

    def get_input_data():
        None