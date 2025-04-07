# pipe_table_widget.py

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QDoubleSpinBox, QSpinBox, QComboBox, QGroupBox,
    QPushButton, QLineEdit, QMessageBox
)
from PyQt6.QtGui import QPixmap, QDoubleValidator
from PyQt6.QtCore import Qt, pyqtSignal

from UI.data.input_variables import *
from UI.extra.local_loss import size_dict_internal_diameter_sch40
from UI.func.pressure_drop.total_head_loss import calculate_pipe_system_head_loss
import numpy as np
import pandas as pd
import logging

class SystemInputWidget(QWidget):
    # Sinal para indicar que o cálculo foi concluído
    calculoCompleto = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Inicializa as listas de spinboxes antes de usar
        self.quantity_suction = []
        self.quantity_discharge = []
        
        # Armazenamento de resultados calculados
        self.system_curve = None
        self.flow_values = None
        self.target_flow = None
        self.suction_friction_loss = None
        self.suction_height = None
        self.npsh_disponivel = None

        # Cria os widgets principais
        suction_group = self._create_group_box("Sucção")
        middle_box = self._create_middle_box()
        discharge_group = self._create_group_box("Recalque")

        # Configura layout dos inputs
        self._setup_input_layout(suction_group, is_suction=True)
        self._setup_input_layout(discharge_group, is_suction=False)

        # Configura layout principal
        main_layout = QVBoxLayout()
        
        # Adiciona grupo de vazão global (acima de tudo)
        flow_group = QGroupBox("Parâmetros do Sistema")
        flow_layout = QVBoxLayout()
        
        # Campo de Vazão (unificado)
        vazao_layout = QHBoxLayout()
        label_vazao = QLabel("Vazão (m³/h):")
        vazao_layout.addWidget(label_vazao)
        
        self.line_edit_vazao = QLineEdit()
        self.line_edit_vazao.setValidator(QDoubleValidator(0.0, 1e9, 2, self))
        self.line_edit_vazao.setPlaceholderText("Informe a vazão do sistema")
        self.line_edit_vazao.textChanged.connect(self.atualizar_velocidades)
        vazao_layout.addWidget(self.line_edit_vazao)
        
        flow_layout.addLayout(vazao_layout)
        flow_group.setLayout(flow_layout)
        main_layout.addWidget(flow_group)
        
        # Layout para os grupos de sucção, meio e recalque
        groups_layout = QHBoxLayout()
        groups_layout.addWidget(suction_group, 3)
        groups_layout.addWidget(middle_box, 6)
        groups_layout.addWidget(discharge_group, 3)
        
        main_layout.addLayout(groups_layout)
        
        # Adiciona o botão Calcular
        calculate_button_layout = QHBoxLayout()
        self.calculate_button = QPushButton("Calcular Curva do Sistema")
        self.calculate_button.setFixedHeight(40)
        self.calculate_button.setStyleSheet("font-weight: bold;")
        self.calculate_button.clicked.connect(self.calcular_sistema)
        calculate_button_layout.addStretch()
        calculate_button_layout.addWidget(self.calculate_button)
        calculate_button_layout.addStretch()
        
        main_layout.addLayout(calculate_button_layout)
        
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
            "Trecho Retilineo": 5,  # metros
            "Diferença de Altura": -3,  # metros
            "Cotovelo 90° Raio Longo": 0,  # quantidade
            "Cotovelo 90° Raio Médio": 0, 
            "Cotovelo 90° Raio Curto": 1,
            "Cotovelo 45°": 0, 
            "Curva 90° Raio Longo": 0, 
            "Curva 90° Raio Curto": 0, 
            "Curva 45°": 0, 
            "Entrada Normal": 0, 
            "Entrada de Borda": 1, 
            "Válvula Gaveta Aberta": 1, 
            "Válvula Globo Aberta": 0, 
            "Válvula Ângular Aberta": 0, 
            "Passagem Reta Tê": 0,
            "Derivação Tê": 0, 
            "Bifurcação Tê": 0, 
            "Válvula de Pé e Crivo": 0,  # quantidade
            "Saída de Canalização": 0, 
            "Válvula de Retenção Leve": 0, 
            "Válvula de Retenção Pesado": 0
        }

        input_values_discharge = {
            "Trecho Retilineo": 87.1,  # metros
            "Diferença de Altura": 22.1,  # metros estimados
            "Cotovelo 90° Raio Longo": 0, 
            "Cotovelo 90° Raio Médio": 0, 
            "Cotovelo 90° Raio Curto": 9,
            "Cotovelo 45°": 0, 
            "Curva 90° Raio Longo": 0, 
            "Curva 90° Raio Curto": 0, 
            "Curva 45°": 0, 
            "Entrada Normal": 0, 
            "Entrada de Borda": 0, 
            "Válvula Gaveta Aberta": 2, 
            "Válvula Globo Aberta": 0,  # registro de globo aberto
            "Válvula Ângular Aberta": 0, 
            "Passagem Reta Tê": 3,
            "Derivação Tê": 0, 
            "Bifurcação Tê": 0, 
            "Válvula de Pé e Crivo": 0, 
            "Saída de Canalização": 0,  # quantidade
            "Válvula de Retenção Leve": 0, 
            "Válvula de Retenção Pesado": 2  # válvula de retenção
        }
        
        # Seleciona os valores apropriados baseado no tipo de entrada
        input_values = input_values_suction if is_suction else input_values_discharge
        
        # Cria layout para o grupo com alinhamento ao topo
        group_layout = QVBoxLayout()
        group_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        group_layout.setSpacing(5)  # Menor espaçamento entre itens
        
        # Configuração para Diâmetro e Velocidade
        params_group = QGroupBox("Parâmetros")
        params_layout = QVBoxLayout()
        
        # Campo de Diâmetro
        diametro_layout = QHBoxLayout()
        label_diametro = QLabel("Diâmetro:")
        diametro_layout.addWidget(label_diametro)
        
        if is_suction:
            self.combo_diametro_suction = QComboBox()
            self.combo_diametro_suction.addItems(list(size_dict_internal_diameter_sch40.keys()))
            self.combo_diametro_suction.currentIndexChanged.connect(lambda: self.atualizar_velocidade("suction"))
            diametro_layout.addWidget(self.combo_diametro_suction)
        else:
            self.combo_diametro_discharge = QComboBox()
            self.combo_diametro_discharge.addItems(list(size_dict_internal_diameter_sch40.keys()))
            self.combo_diametro_discharge.currentIndexChanged.connect(lambda: self.atualizar_velocidade("discharge"))
            diametro_layout.addWidget(self.combo_diametro_discharge)
        
        params_layout.addLayout(diametro_layout)
        
        # Campo de Velocidade
        velocidade_layout = QHBoxLayout()
        label_velocidade = QLabel("Velocidade (m/s):")
        velocidade_layout.addWidget(label_velocidade)
        
        if is_suction:
            self.line_edit_velocity_suction = QLineEdit()
            self.line_edit_velocity_suction.setReadOnly(True)
            self.line_edit_velocity_suction.setPlaceholderText("Calculado automaticamente")
            velocidade_layout.addWidget(self.line_edit_velocity_suction)
        else:
            self.line_edit_velocity_discharge = QLineEdit()
            self.line_edit_velocity_discharge.setReadOnly(True)
            self.line_edit_velocity_discharge.setPlaceholderText("Calculado automaticamente")
            velocidade_layout.addWidget(self.line_edit_velocity_discharge)
        
        params_layout.addLayout(velocidade_layout)
        
        # Se for sucção, adiciona campo de NPSH disponível
        if is_suction:
            npsh_layout = QHBoxLayout()
            label_npsh = QLabel("NPSH Disponível (m):")
            npsh_layout.addWidget(label_npsh)
            
            self.line_edit_npsh = QLineEdit()
            self.line_edit_npsh.setReadOnly(True)
            self.line_edit_npsh.setPlaceholderText("Será calculado")
            npsh_layout.addWidget(self.line_edit_npsh)
            
            params_layout.addLayout(npsh_layout)
        
        params_group.setLayout(params_layout)
        group_layout.addWidget(params_group)
        
        # Adiciona componentes em um grupo separado
        components_group = QGroupBox("Componentes")
        components_layout = QVBoxLayout()
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 5)
        
        desc_label = QLabel("Descrição")
        desc_label.setFixedHeight(20)  # Altura fixa para o header
        
        quant_label = QLabel("Quantidade")
        quant_label.setFixedHeight(20)  # Altura fixa para o header
        
        header_layout.addWidget(desc_label, 2)
        header_layout.addWidget(quant_label, 1)
        components_layout.addLayout(header_layout)
        
        # Adiciona inputs para os componentes
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
                input_spin_box.setSingleStep(0.05)
                input_spin_box.setMaximum(999999)
            
            # Configurações para Diferença de Altura (permitir valores negativos)
            if label == "Diferença de Altura":
                input_spin_box.setMinimum(-999)  # Permitir valores negativos até -100m
                input_spin_box.setMaximum(999)   # Permitir valores positivos até 100m
                input_spin_box.setDecimals(2)    # Permitir 2 casas decimais
                
                # Tooltips diferentes para sucção e recalque
                if is_suction:
                    tooltip = "Valores positivos: bomba afogada (nível do fluido acima da sucção)\nValores negativos: nível do fluido abaixo da sucção da bomba"
                    input_spin_box.setToolTip(tooltip)
                    input_label.setToolTip(tooltip)
                else:
                    tooltip = "Diferença de altura do recalque (positiva quando o fluido sobe, negativa quando desce)"
                    input_spin_box.setToolTip(tooltip)
                    input_label.setToolTip(tooltip)
                
            # Adiciona ao layout com proporções 2:1 para os campos
            h_layout.addWidget(input_label, 2)
            h_layout.addWidget(input_spin_box, 1)
            h_layout.setContentsMargins(0, 0, 0, 0)  # Remove margens extras
            components_layout.addLayout(h_layout)
            
            # Adiciona à lista apropriada
            if is_suction:
                self.quantity_suction.append(input_spin_box)
            else:
                self.quantity_discharge.append(input_spin_box)
        
        # Adiciona um stretchAtEnd para garantir que o espaço em branco fique na parte inferior
        components_layout.addStretch(1)
        
        components_group.setLayout(components_layout)
        group_layout.addWidget(components_group)
        
        # Define o layout do grupo
        group_box.setLayout(group_layout)

    def atualizar_velocidades(self):
        """Atualiza as velocidades tanto para sucção quanto para recalque"""
        self.atualizar_velocidade("suction")
        self.atualizar_velocidade("discharge")

    def atualizar_velocidade(self, section):
        """
        Calcula e atualiza a velocidade do fluido com base na vazão e no diâmetro selecionado.
        
        Parâmetros:
            section: "suction" ou "discharge" para indicar qual seção atualizar
        """
        try:
            # Usar a vazão unificada para ambos
            q_m3_h = float(self.line_edit_vazao.text())
            
            if section == "suction":
                selected_size = self.combo_diametro_suction.currentText()
                line_edit_velocity = self.line_edit_velocity_suction
            else:  # discharge
                selected_size = self.combo_diametro_discharge.currentText()
                line_edit_velocity = self.line_edit_velocity_discharge
        except ValueError:
            # Se a vazão não for um número válido, limpa os campos de velocidade
            self.line_edit_velocity_suction.setText("")
            self.line_edit_velocity_discharge.setText("")
            return
        
        # Converte vazão de m³/h para m³/s
        q_m3_s = q_m3_h / 3600.0
        
        try:
            d = size_dict_internal_diameter_sch40[selected_size] * 0.001  # Converte para metros
        except KeyError:
            print(f"Chave não encontrada para o diâmetro: {selected_size}, utilizando valor padrão 0.05 m")
            d = 0.05  # Valor padrão se não encontrado
        
        # Calcula a área e a velocidade
        area = np.pi * (d / 2) ** 2
        velocity = q_m3_s / area
        
        line_edit_velocity.setText(f"{velocity:.2f}")
    
    def calcular_pressao_vapor(self, temperatura):
        """
        Calcula a pressão de vapor da água com base na temperatura.
        Esta é uma aproximação para água entre 0°C e 100°C.
        
        Parâmetros:
            temperatura: Temperatura da água em °C
            
        Retorna:
            Pressão de vapor em Pa
        """
        # Equação aproximada para pressão de vapor da água
        # Baseada na equação de Antoine (simplificada)
        # Válida para água entre 0°C e 100°C
        if temperatura < 0 or temperatura > 100:
            QMessageBox.warning(self, "Aviso", "Temperatura fora do intervalo válido (0-100°C).")
            temperatura = max(0, min(temperatura, 100))
        
        # Valores aproximados para água com base na equação de Antoine
        if temperatura <= 60:
            # Aproximação para 0-60°C
            pressao_vapor = 10**(8.07131 - 1730.63/(233.426 + temperatura)) * 133.322
        else:
            # Aproximação para 61-100°C
            pressao_vapor = 10**(8.14019 - 1810.94/(244.485 + temperatura)) * 133.322
        
        return pressao_vapor
    
    def calcular_npsh_disponivel(self, suction_height, suction_friction_loss, flow_values=None):
        """
        Calcula o NPSH disponível do sistema para uma faixa de vazões.
        
        NPSH_d = P_atm/ρg + h_s - h_v - h_f_sucção(Q)
        
        Onde:
        - P_atm: pressão atmosférica (Pa)
        - ρ: densidade do fluido (kg/m³)
        - g: aceleração da gravidade (9.81 m/s²)
        - h_s: altura estática da sucção (m)
        - h_v: pressão de vapor do fluido (m coluna de fluido)
        - h_f_sucção(Q): perda de carga na linha de sucção em função da vazão (m)
        
        Parâmetros:
            suction_height: Altura estática da sucção (m)
            suction_friction_loss: Perda de carga na linha de sucção para vazão de projeto (m)
            flow_values: Array de valores de vazão para cálculo da curva (opcional)
            
        Retorna:
            Se flow_values for None: NPSH disponível em metros para a vazão de projeto
            Se flow_values for fornecido: Array com valores de NPSH disponível para cada vazão
        """
        try:
            # Obter acesso ao widget de propriedades do fluido
            main_window = self.window()
            fluid_prop_widget = main_window.fluid_prop_input_widget
            
            # Obter densidade do fluido
            rho = fluid_prop_widget.get_rho_input_value()  # kg/m³
            
            # Pressão atmosférica padrão ao nível do mar (101325 Pa)
            p_atm = 101325  # Pa
            
            # Pressão de vapor do fluido - baseada na temperatura
            temperatura = fluid_prop_widget.temperature_input.value()  # °C
            p_vapor = self.calcular_pressao_vapor(temperatura)  # Pa
            
            # Converter pressões para metros de coluna de fluido
            h_atm = p_atm / (rho * 9.81)
            h_vapor = p_vapor / (rho * 9.81)
            
            logging.info(f"Altura equivalente atmosférica: {h_atm:.2f} m")
            logging.info(f"Altura equivalente da pressão de vapor: {h_vapor:.2f} m")
            logging.info(f"Altura estática da sucção: {suction_height:.2f} m")
            logging.info(f"Perda de carga na vazão de projeto: {suction_friction_loss:.2f} m")
            
            # Se não forneceu vazões, retorna apenas para a vazão de projeto
            if flow_values is None:
                npsh_disponivel = h_atm + suction_height - h_vapor - suction_friction_loss
                logging.info(f"NPSH disponível calculado (ponto único): {npsh_disponivel:.2f} m")
                return npsh_disponivel
            
            # Caso contrário, calcula para cada vazão
            # Precisamos escalar a perda de carga de acordo com a lei quadrática (Q²)
            vazao_projeto = float(self.line_edit_vazao.text())
            
            # Verificar se a vazão de projeto é válida
            if vazao_projeto <= 0:
                logging.warning("Vazão de projeto inválida, usando 1.0 m³/h como fallback")
                vazao_projeto = 1.0
            
            # Array para armazenar valores de NPSH
            npsh_values = np.zeros_like(flow_values)
            
            # Filtrar valores negativos ou zero (para evitar problemas no cálculo)
            valid_indices = flow_values > 0
            
            # Para valores válidos, calcular NPSH disponível
            for i, vazao in enumerate(flow_values):
                if vazao > 0:  # Evitar divisão por zero
                    # A perda de carga varia com o quadrado da vazão
                    perda_carga_proporcional = suction_friction_loss * (vazao / vazao_projeto) ** 2
                    
                    # Cálculo do NPSH disponível para cada vazão
                    npsh_values[i] = h_atm + suction_height - h_vapor - perda_carga_proporcional
                else:
                    # Para vazão zero, a perda de carga é zero
                    npsh_values[i] = h_atm + suction_height - h_vapor
            
            # Log dos resultados para depuração
            min_npsh = np.min(npsh_values)
            max_npsh = np.max(npsh_values)
            logging.info(f"Curva de NPSH disponível calculada: {len(npsh_values)} pontos, range [{min_npsh:.2f}, {max_npsh:.2f}]")
            
            return npsh_values
            
        except Exception as e:
            logging.error(f"Erro ao calcular NPSH disponível: {e}", exc_info=True)
            
            # Em caso de erro, retorna um valor padrão ou array de zeros
            if flow_values is None:
                return 0.0
            else:
                return np.zeros_like(flow_values)


    
    def calcular_sistema(self):
        """
        Executa o cálculo do sistema utilizando os valores dos widgets,
        calcula a curva do sistema e o NPSH disponível.
        """
        # Verificar se o campo de vazão está preenchido
        try:
            self.target_flow = float(self.line_edit_vazao.text())
        except ValueError:
            QMessageBox.critical(self, "Erro", "Por favor, preencha o campo de vazão corretamente.")
            return False
        
        # Obter acesso ao widget de propriedades do fluido
        main_window = self.window()
        fluid_prop_widget = main_window.fluid_prop_input_widget
        
        # Obter os valores dos spinboxes
        spinbox_suction = self.get_spinbox_values_suction()
        spinbox_discharge = self.get_spinbox_values_discharge()
        
        # Obter tamanhos selecionados
        suction_size = self.combo_diametro_suction.currentText()
        discharge_size = self.combo_diametro_discharge.currentText()
        
        # Obter viscosidade, densidade e rugosidade
        mu_value = fluid_prop_widget.get_mu_input_value()
        rho_value = fluid_prop_widget.get_rho_input_value()
        roughness = fluid_prop_widget.get_roughness_value()  # Obtém o valor de rugosidade do tubo em mm
        
        try:
            # Calcular a curva do sistema
            result = calculate_pipe_system_head_loss(
                spinbox_suction, suction_size,
                spinbox_discharge, discharge_size,
                self.target_flow, mu_value, rho_value, roughness/1000  # Converte rugosidade de mm para m
            )
            
            # Desempacotar resultados
            head_values_coef, min_flow, max_flow, suction_friction_loss, suction_height = result
            
            # Armazenar valores para uso posterior
            self.system_curve = head_values_coef
            self.suction_friction_loss = suction_friction_loss
            self.suction_height = suction_height
            
            logging.info(f"Sistema calculado - Coeficientes: {head_values_coef}")
            logging.info(f"Perda de carga na sucção: {suction_friction_loss:.2f} m")
            logging.info(f"Altura estática da sucção: {suction_height:.2f} m")
            
            # Calcular o NPSH disponível no ponto de projeto
            self.npsh_disponivel = self.calcular_npsh_disponivel(suction_height, suction_friction_loss)
            
            # Atualizar o campo de NPSH disponível
            self.line_edit_npsh.setText(f"{self.npsh_disponivel:.2f}")
            
            # Mostrar mensagem de sucesso
            QMessageBox.information(
                self, 
                "Cálculo Concluído", 
                f"Cálculo do sistema concluído com sucesso!\n\n"
                f"NPSH Disponível: {self.npsh_disponivel:.2f} m"
            )
            
            # Emitir sinal indicando que o cálculo foi concluído
            self.calculoCompleto.emit()
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao calcular o sistema: {str(e)}")
            logging.error(f"Erro no cálculo do sistema: {e}", exc_info=True)
            return False

    def get_spinbox_values_suction(self):
        """Retorna os valores dos spinboxes de sucção"""
        return [spin_box.value() for spin_box in self.quantity_suction]

    def get_spinbox_values_discharge(self):
        """Retorna os valores dos spinboxes de recalque"""
        return [spin_box.value() for spin_box in self.quantity_discharge]

    def get_suction_size(self):
        """Retorna o tamanho selecionado para sucção"""
        return self.combo_diametro_suction.currentText()

    def get_discharge_size(self):
        """Retorna o tamanho selecionado para recalque"""
        return self.combo_diametro_discharge.currentText()
    
    def get_target_flow(self):
        """Retorna a vazão utilizada para o cálculo"""
        return self.target_flow
    
    def get_system_curve(self):
        """Retorna os coeficientes da curva do sistema"""
        return self.system_curve
    
    def get_npsh_disponivel(self, flow_values=None):
        """
        Retorna o NPSH disponível calculado.
        Se flow_values for fornecido, retorna a curva de NPSH disponível para essas vazões.
        
        Parâmetros:
            flow_values: Array de valores de vazão (opcional)
            
        Retorna:
            Se flow_values for None: Valor fixo do NPSH disponível no ponto de projeto
            Se flow_values for fornecido: Array de valores de NPSH disponível para cada vazão
        """
        try:
            # Verificar se temos os dados necessários para o cálculo
            if not hasattr(self, 'suction_height') or not hasattr(self, 'suction_friction_loss'):
                logging.warning("Dados de sistema não disponíveis para calcular NPSH disponível variável")
                
                # Se não temos os dados necessários, retornar o valor fixo
                if flow_values is None:
                    return self.npsh_disponivel
                else:
                    # Retornar um array constante com o valor fixo
                    return np.full_like(flow_values, self.npsh_disponivel)
            
            if flow_values is None:
                return self.npsh_disponivel
            else:
                # Calcular NPSH disponível para os valores de vazão fornecidos
                npsh_curva = self.calcular_npsh_disponivel(self.suction_height, self.suction_friction_loss, flow_values)
                
                # Log básico para depuração
                if npsh_curva is not None and len(npsh_curva) > 0:
                    logging.info(f"Retornando curva de NPSH disponível com {len(npsh_curva)} pontos: [{np.min(npsh_curva):.2f}, {np.max(npsh_curva):.2f}]")
                else:
                    logging.warning("Curva de NPSH disponível não calculada corretamente")
                    
                return npsh_curva
        except Exception as e:
            logging.error(f"Erro em get_npsh_disponivel: {e}", exc_info=True)
            
            # Em caso de erro, retornar um valor padrão ou array de zeros
            if flow_values is None:
                return 0.0
            else:
                return np.zeros_like(flow_values)

