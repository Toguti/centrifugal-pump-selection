import sys
import os
import sqlite3
import json
import numpy as np
import logging
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QApplication, QDialog, QTableWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QWidget, QFormLayout, QPushButton,
    QStyledItemDelegate, QGroupBox, QListWidget, QMessageBox,
    QListWidgetItem, QComboBox
)
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from typing import Dict, Any, Tuple, List, Optional, Union

# Importação da função de seleção automática de bomba e da função de cálculo de interseções
from UI.func.auto_pump_selection import auto_pump_selection, find_intersection_points


class FloatDelegate(QStyledItemDelegate):
    """Delegate para restringir a edição da célula a valores float."""
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(QDoubleValidator(editor))
        return editor


class CurveInputDialog(QDialog):
    """Janela para entrada de pontos da curva da bomba."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Curva da Bomba")
        self.setGeometry(500, 500, 1200, 800)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface de usuário do diálogo."""
        # Layout principal
        vertical_layout = QVBoxLayout(self)
        
        # Instruções
        instruction_label = QLabel("Preencha a tabela com os pontos da curva característica da bomba.", self)
        vertical_layout.addWidget(instruction_label)
        
        # Layout horizontal para formulário e tabela
        horizontal_layout = QHBoxLayout()
        vertical_layout.addLayout(horizontal_layout)
        
        # Configuração do formulário de informações da bomba
        self.setup_pump_info_form(horizontal_layout)
        
        # Configuração da tabela de pontos da curva
        self.setup_curve_table(horizontal_layout)
        
        # Definir proporções para o layout horizontal
        horizontal_layout.setStretch(0, 3)  # Formulário
        horizontal_layout.setStretch(1, 7)  # Tabela
    
    def setup_pump_info_form(self, parent_layout):
        """Configura o formulário de informações da bomba."""
        pump_info_widget = QWidget(self)
        pump_info_layout = QFormLayout(pump_info_widget)
        
        # Campos do formulário
        self.line_edit_marca = QLineEdit(pump_info_widget)
        pump_info_layout.addRow("Marca:", self.line_edit_marca)
        
        self.line_edit_modelo = QLineEdit(pump_info_widget)
        pump_info_layout.addRow("Modelo:", self.line_edit_modelo)
        
        self.line_edit_diametro = QLineEdit(pump_info_widget)
        self.line_edit_diametro.setValidator(QIntValidator(0, 1000000, self))
        pump_info_layout.addRow("Diâmetro:", self.line_edit_diametro)
        
        self.line_edit_rotacao = QLineEdit(pump_info_widget)
        self.line_edit_rotacao.setValidator(QIntValidator(0, 1000000, self))
        pump_info_layout.addRow("Rotação:", self.line_edit_rotacao)
        
        # Botão para adicionar bomba
        self.btn_adicionar_bomba = QPushButton("Adicionar Bomba", pump_info_widget)
        self.btn_adicionar_bomba.clicked.connect(self.adicionar_bomba)
        pump_info_layout.addRow(self.btn_adicionar_bomba)
        
        parent_layout.addWidget(pump_info_widget)
    
    def setup_curve_table(self, parent_layout):
        """Configura a tabela de pontos da curva."""
        self.table_widget = QTableWidget(6, 5, self)
        headers = ["Vazão", "Head", "Eficiência", "NPSHr", "Potência"]
        self.table_widget.setHorizontalHeaderLabels(headers)
        self.table_widget.setItemDelegate(FloatDelegate(self.table_widget))
        parent_layout.addWidget(self.table_widget)
    
    def adicionar_bomba(self):
        """Adiciona a bomba ao banco de dados."""
        # TODO: Implementar a adição da bomba ao banco de dados
        QMessageBox.information(self, "Sucesso", "Bomba adicionada com sucesso!")


class PumpSelectionWidget(QWidget):
    """
    Widget para gerenciamento e seleção de bombas.
    Obtém os dados do SystemInputWidget para a seleção de bombas.
    """
    def __init__(self, system_input_widget, fluid_prop_input_widget, parent=None):
        super().__init__(parent)
        self.system_input_widget = system_input_widget
        self.fluid_prop_input_widget = fluid_prop_input_widget
        self.system_curve = None
        self.system_curve_adjusted = None
        self.target_flow = None
        self.pumps = []
        self.selected_pump_index = None
        
        # Conectar ao sinal de cálculo concluído do SystemInputWidget
        self.system_input_widget.calculoCompleto.connect(self.atualizar_dados_sistema)
        
        self.init_ui()
        self.setup_db_timer()
    
    def init_ui(self):
        """Inicializa a interface de usuário do widget."""
        self.setWindowTitle("Seleção de Bombas")
        self.resize(800, 600)
        
        # Layout principal
        main_layout = QHBoxLayout(self)
        
        # Configuração do painel esquerdo (controles e informações)
        left_widget = self.setup_left_panel()
        
        # Configuração do painel direito (gráfico)
        right_widget = self.setup_right_panel()
        
        # Adicionar os painéis ao layout principal
        main_layout.addWidget(left_widget, 3)
        main_layout.addWidget(right_widget, 7)
    
    def setup_left_panel(self) -> QWidget:
        """Configura o painel esquerdo com controles e informações."""
        left_widget = QWidget(self)
        left_layout = QVBoxLayout(left_widget)
        
        # Grupo de informações do sistema
        system_info_group = self.setup_system_info_group()
        left_layout.addWidget(system_info_group)
        
        # Grupo de seleção de bomba
        self.pump_list_box = self.setup_pump_list_group()
        left_layout.addWidget(self.pump_list_box)
        
        # Grupo de dados da bomba selecionada
        self.pump_data_box = self.setup_pump_data_group()
        left_layout.addWidget(self.pump_data_box)
        
        left_layout.addStretch()
        
        # Botões de ação
        button_layout = QHBoxLayout()
        self.btn_adicionar_curva = QPushButton("Adicionar Nova Curva", left_widget)
        self.btn_adicionar_curva.clicked.connect(self.abrir_curve_input_dialog)
        button_layout.addWidget(self.btn_adicionar_curva)
        left_layout.addLayout(button_layout)
        
        return left_widget
    
    def setup_system_info_group(self) -> QGroupBox:
        """Configura o grupo de informações do sistema."""
        system_info_group = QGroupBox("Informações do Sistema", self)
        system_info_layout = QFormLayout(system_info_group)
        
        # Campo de vazão total
        self.system_target_flow = QLineEdit()
        self.system_target_flow.setReadOnly(True)
        system_info_layout.addRow("Vazão Total do Sistema:", self.system_target_flow)
        
        # Campo de head de projeto
        self.system_head = QLineEdit()
        self.system_head.setReadOnly(True)
        system_info_layout.addRow("Head de Projeto:", self.system_head)
        
        # Campo de NPSH disponível
        self.system_npsh_disponivel = QLineEdit()
        self.system_npsh_disponivel.setReadOnly(True)
        system_info_layout.addRow("NPSH Disponível:", self.system_npsh_disponivel)
        
        # Combo para número de bombas em paralelo
        label_n_bombas = QLabel("N° de Bombas em Paralelo:")
        self.combo_n_bombas = QComboBox()
        self.combo_n_bombas.addItems([str(i) for i in range(1, 10)])
        self.combo_n_bombas.currentIndexChanged.connect(self.atualizar_grafico_bombas_paralelo)
        system_info_layout.addRow(label_n_bombas, self.combo_n_bombas)
        
        # Campo para vazão por bomba
        self.vazao_por_bomba = QLineEdit()
        self.vazao_por_bomba.setReadOnly(True)
        system_info_layout.addRow("Vazão por Bomba de Projeto:", self.vazao_por_bomba)
        
        return system_info_group
    
    def setup_pump_list_group(self) -> QGroupBox:
        """Configura o grupo de seleção de bomba."""
        pump_list_box = QGroupBox("Seleção de Bomba", self)
        list_layout = QVBoxLayout(pump_list_box)
        
        # Botão para selecionar bomba
        self.btn_selecionar_bomba = QPushButton("Selecionar Bomba", pump_list_box)
        self.btn_selecionar_bomba.clicked.connect(self.selecionar_bomba)
        list_layout.addWidget(self.btn_selecionar_bomba)
        
        # Lista de bombas
        self.list_widget = QListWidget(pump_list_box)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        list_layout.addWidget(self.list_widget)
        
        return pump_list_box
    
    def setup_pump_data_group(self) -> QGroupBox:
        """Configura o grupo de dados da bomba selecionada."""
        pump_data_box = QGroupBox("Dados da Bomba", self)
        data_layout = QFormLayout(pump_data_box)
        
        # Campos de informação
        self.result_flow = QLineEdit()
        self.result_flow.setReadOnly(True)
        data_layout.addRow("Vazão:", self.result_flow)
        
        self.result_head = QLineEdit()
        self.result_head.setReadOnly(True)
        data_layout.addRow("Head:", self.result_head)
        
        self.result_pump = QLineEdit()
        self.result_pump.setReadOnly(True)
        data_layout.addRow("Bomba (Marca/Modelo):", self.result_pump)
        
        self.result_rotor_diametro = QLineEdit()
        self.result_rotor_diametro.setReadOnly(True)
        data_layout.addRow("Diâmetro do rotor:", self.result_rotor_diametro)
        
        self.result_eff = QLineEdit()
        self.result_eff.setReadOnly(True)
        data_layout.addRow("Eficiência:", self.result_eff)
        
        self.result_power = QLineEdit()
        self.result_power.setReadOnly(True)
        data_layout.addRow("Potência Absorvida:", self.result_power)
        
        self.result_npsh = QLineEdit()
        self.result_npsh.setReadOnly(True)
        data_layout.addRow("NPSH Requerido:", self.result_npsh)
        
        self.result_npsh_comparison = QLineEdit()
        self.result_npsh_comparison.setReadOnly(True)
        data_layout.addRow("Margem de NPSH:", self.result_npsh_comparison)
        
        return pump_data_box
    
    def setup_right_panel(self) -> QWidget:
        """Configura o painel direito com o gráfico."""
        right_widget = QWidget(self)
        right_layout = QVBoxLayout(right_widget)
        
        # Configuração do gráfico
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("Vazão (m³/h)")
        self.ax.set_ylabel("Head (m)")
        self.ax.set_title("Curva do Sistema x Curva da Bomba")
        self.canvas.draw()
        
        right_layout.addWidget(self.canvas)
        
        return right_widget
    
    def setup_db_timer(self):
        """Configura um timer para monitorar alterações no banco de dados."""
        self.last_db_mod_time = os.path.getmtime("./src/db/pump_data.db")
        self.timer = QTimer(self)
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.check_db_update)
        self.timer.start()
    
    def check_db_update(self):
        """Verifica se o banco de dados foi atualizado."""
        try:
            current_mod_time = os.path.getmtime("./src/db/pump_data.db")
            if current_mod_time != self.last_db_mod_time:
                self.last_db_mod_time = current_mod_time
                # Recarregar bombas se necessário
                if self.system_curve is not None and self.target_flow is not None:
                    self.selecionar_bomba()
        except Exception as e:
            logging.error(f"Erro ao verificar atualização do banco de dados: {e}")
    
    def atualizar_dados_sistema(self):
        """Atualiza os dados do sistema após o cálculo no SystemInputWidget."""
        self.system_curve = self.system_input_widget.get_system_curve()
        self.target_flow = self.system_input_widget.get_target_flow()
        npsh_disponivel = self.system_input_widget.get_npsh_disponivel()
        
        # Atualizar campos na interface
        if self.target_flow is not None:
            self.system_target_flow.setText(f"{self.target_flow:.2f} m³/h")
            
            # Calcular o head no ponto de operação
            if self.system_curve is not None:
                head_valor = np.polyval(self.system_curve, self.target_flow)
                self.system_head.setText(f"{head_valor:.2f} m")
        
        if npsh_disponivel is not None:
            self.system_npsh_disponivel.setText(f"{npsh_disponivel:.2f} m")
        
        # Atualizar vazão por bomba
        self.atualizar_vazao_por_bomba()
        
        # Habilitar o botão de seleção de bomba
        self.btn_selecionar_bomba.setEnabled(True)
        
        # Atualizar o gráfico
        self.atualizar_grafico_bombas_paralelo()
    
    def atualizar_vazao_por_bomba(self):
        """Atualiza o campo de vazão por bomba com base no número de bombas em paralelo."""
        if self.target_flow is None:
            return
            
        n_bombas = int(self.combo_n_bombas.currentText())
        vazao_por_bomba = self.target_flow / n_bombas
        self.vazao_por_bomba.setText(f"{vazao_por_bomba:.2f} m³/h")
    
    def atualizar_grafico_bombas_paralelo(self):
        """
        Atualiza o gráfico quando o número de bombas em paralelo é alterado.
        Limpa a seleção de bombas atual e exibe apenas a curva do sistema.
        """
        # Verificar se temos dados do sistema
        if self.system_curve is None or self.target_flow is None:
            return
            
        # Obter o número de bombas em paralelo
        n_bombas = int(self.combo_n_bombas.currentText())
        
        # Calcular a vazão por bomba
        vazao_por_bomba = self.target_flow / n_bombas
        
        # Atualizar os campos de texto
        suffix = 's' if n_bombas > 1 else ''
        self.system_target_flow.setText(f"{self.target_flow:.2f} m³/h (total para {n_bombas} bomba{suffix})")
        self.vazao_por_bomba.setText(f"{vazao_por_bomba:.2f} m³/h por bomba")
        
        # Ajustar a curva do sistema para o número atual de bombas
        self.system_curve_adjusted = self.adjust_system_curve_for_parallel_pumps(self.system_curve, n_bombas)
        
        # Limpar a seleção atual
        self.limpar_selecao_bomba()
        
        # Criar flow_values para o gráfico
        flow_values = np.linspace(0, self.target_flow * 1.4, 500)
        
        # Mostrar apenas a curva do sistema (sem bomba selecionada)
        self.atualizar_plot(flow_values, self.system_curve)
    
    def limpar_selecao_bomba(self):
        """Limpa a seleção de bomba atual e os campos relacionados."""
        # Limpar a lista de bombas
        self.list_widget.clear()
        self.pumps = []
        self.selected_pump_index = None
        
        # Limpar os campos de informação da bomba
        self.result_flow.setText("")
        self.result_head.setText("")
        self.result_pump.setText("")
        self.result_eff.setText("")
        self.result_power.setText("")
        self.result_npsh.setText("")
        self.result_rotor_diametro.setText("")
        self.result_npsh_comparison.setText("")
    
    def extrair_valores_intersecao(self, pump: Dict[str, Any], system_curve: Optional[np.ndarray] = None) -> Tuple[float, float]:
        """
        Extrai os valores de vazão e head a partir dos pontos de interseção.
        
        Parâmetros:
            pump: Dicionário com dados da bomba
            system_curve: Coeficientes da curva do sistema (opcional)
            
        Retorna:
            Tupla (vazao_bomba, head_value)
        """
        try:
            # Verificar se já temos os valores calculados
            if 'vazao_bomba' in pump and 'head_value' in pump:
                return pump['vazao_bomba'], pump['head_value']
            
            # Extrair valores das interseções
            intersecoes = pump.get('intersecoes', [[0.0, 0.0]])
            vazao_bomba = 0.0
            head_value = 0.0
            
            if isinstance(intersecoes, list) and len(intersecoes) > 0:
                if isinstance(intersecoes[0], list) and len(intersecoes[0]) > 0:
                    vazao_bomba = intersecoes[0][0]  # Estrutura: [[x, y], ...]
                    if len(intersecoes[0]) > 1:
                        head_value = intersecoes[0][1]
                    elif system_curve is not None:
                        head_value = np.polyval(system_curve, vazao_bomba)
                else:
                    vazao_bomba = intersecoes[0]  # Estrutura: [x, y, ...]
                    if len(intersecoes) > 1:
                        head_value = intersecoes[1]
                    elif system_curve is not None:
                        head_value = np.polyval(system_curve, vazao_bomba)
            
            return vazao_bomba, head_value
            
        except Exception as e:
            logging.error(f"Erro ao extrair valores de interseção: {e}")
            return 0.0, 0.0
    
    def formatar_item_lista(self, pump: Dict[str, Any]) -> Tuple[str, str]:
        """
        Formata o texto do item e o tooltip a partir dos dados da bomba.
        
        Parâmetros:
            pump: Dicionário com dados da bomba
            
        Retorna:
            Tupla (item_text, tooltip_text)
        """
        # Obter o número de bombas em paralelo
        n_bombas = int(self.combo_n_bombas.currentText())
        
        # Valores da bomba
        vazao_bomba = pump.get('vazao_bomba', 0.0)
        vazao_total = vazao_bomba * n_bombas
        
        # Texto do item
        item_text = (f"Marca: {pump.get('marca', 'N/D')}, Modelo: {pump.get('modelo', 'N/D')}, "
                    f"Diâmetro: {pump.get('diametro', 'N/D')}, Rotação: {pump.get('rotacao', 'N/D')}, "
                    f"Eff.: {pump.get('pump_eff', 0):.2f}%")
        
        # NPSH
        npsh_disponivel = self.system_input_widget.get_npsh_disponivel()
        margem_npsh = npsh_disponivel - pump.get('pump_npshr', 0) if npsh_disponivel is not None else 0
        
        # Texto do tooltip
        tooltip_text = (f"Vazão Total: {vazao_total:.2f} m³/h\n"
                        f"Vazão por Bomba: {vazao_bomba:.2f} m³/h\n"
                        f"Rotação: {pump.get('rotacao', 'N/D')} rpm\n"
                        f"NPSHr: {pump.get('pump_npshr', 0):.1f} m\n"
                        f"Potência: {pump.get('pump_power', 0):.1f} cv (por bomba)\n"
                        f"Potência Total: {pump.get('pump_power', 0) * n_bombas:.1f} cv ({n_bombas} bombas)\n"
                        f"NPSH Disponível: {npsh_disponivel:.1f} m\n"
                        f"Margem de NPSH: {margem_npsh:.1f} m\n"
                        f"Bombas em Paralelo: {n_bombas}")
        
        return item_text, tooltip_text
    
    def selecionar_bomba(self) -> None:
        """
        Executa a seleção de bombas com base nos dados do sistema calculados previamente.
        Considera o número de bombas em paralelo para a seleção.
        Filtra as bombas que não atendem ao critério de NPSH.
        """
        # Verificar pré-condições
        if not self.verificar_precondições_selecao():
            return
        
        # Obter parâmetros do sistema
        npsh_disponivel = self.system_input_widget.get_npsh_disponivel()
        n_bombas = int(self.combo_n_bombas.currentText())
        vazao_por_bomba = self.target_flow / n_bombas
        
        # Logging de parâmetros
        self.logar_parametros_selecao(npsh_disponivel, n_bombas, vazao_por_bomba)
        
        # Ajustar curva do sistema para bombas em paralelo
        system_curve_adjusted = self.adjust_system_curve_for_parallel_pumps(self.system_curve, n_bombas)
        self.system_curve_adjusted = system_curve_adjusted
        
        # Selecionar bombas usando auto_pump_selection
        pumps = auto_pump_selection(system_curve_adjusted, vazao_por_bomba)
        
        # Reset da interface
        self.list_widget.clear()
        self.selected_pump_index = None
        
        # Verificar se há bombas disponíveis
        if isinstance(pumps, str):
            self.list_widget.addItem(pumps)
            self.pumps = []
            return
        
        # Processar e filtrar bombas
        self.processar_bombas(pumps, npsh_disponivel, vazao_por_bomba, n_bombas)
    
    def verificar_precondições_selecao(self) -> bool:
        """Verifica as pré-condições para a seleção de bombas."""
        if self.system_curve is None or self.target_flow is None:
            QMessageBox.warning(
                self, 
                "Aviso", 
                "É necessário calcular o sistema primeiro. Vá para a aba 'Sistema' e clique em 'Calcular Curva do Sistema'."
            )
            return False
        
        npsh_disponivel = self.system_input_widget.get_npsh_disponivel()
        if npsh_disponivel is None or npsh_disponivel <= 0:
            QMessageBox.critical(self, "Erro", "NPSH disponível não calculado ou inválido.")
            return False
        
        return True
    
    def logar_parametros_selecao(self, npsh_disponivel, n_bombas, vazao_por_bomba):
        """Registra os parâmetros de seleção no log."""
        logging.info(f"NPSH disponível utilizado: {npsh_disponivel:.2f} m")
        logging.info(f"Número de bombas em paralelo: {n_bombas}")
        logging.info(f"Vazão total do sistema: {self.target_flow:.2f} m³/h")
        logging.info(f"Vazão alvo por bomba: {vazao_por_bomba:.2f} m³/h")
    
    def processar_bombas(self, pumps, npsh_disponivel, vazao_por_bomba, n_bombas):
        """Processa e filtra as bombas com base no NPSH disponível."""
        # Filtrar bombas com base no critério NPSH
        pumps_filtered = []
        filtered_out_count = 0
        
        for pump in pumps:
            # Verificar se o NPSH requerido da bomba é menor que o NPSH disponível
            if pump['pump_npshr'] < npsh_disponivel:
                # Calcular e armazenar valores do ponto de operação
                self.calcular_ponto_operacao(pump, n_bombas)
                pumps_filtered.append(pump)
            else:
                filtered_out_count += 1
                logging.info(f"Bomba filtrada por NPSH: {pump['marca']} {pump['modelo']} - "
                            f"NPSHr: {pump['pump_npshr']:.2f} m > NPSHd: {npsh_disponivel:.2f} m")
        
        logging.info(f"Bombas removidas pelo filtro NPSH: {filtered_out_count}")
        
        # Verificar se há bombas após filtragem
        if not pumps_filtered:
            self.list_widget.addItem("Nenhuma bomba atende ao critério de NPSH disponível.")
            self.pumps = []
            return
        
        # Ordenar bombas pela proximidade ao target_flow (vazão por bomba)
        try:
            pumps_sorted = sorted(
                pumps_filtered,
                key=lambda p: abs(p.get('vazao_bomba', 0) - vazao_por_bomba)
            )
        except Exception as e:
            logging.error(f"Erro ao ordenar bombas: {e}")
            pumps_sorted = pumps_filtered
        
        self.pumps = pumps_sorted
        
        # Adicionar bombas à lista
        self.atualizar_lista_bombas()
    
    def calcular_ponto_operacao(self, pump, n_bombas):
        """
        Calcula o ponto de operação da bomba.
        Usa diretamente as informações de interseção fornecidas por auto_pump_selection.
        """
        try:
            # Extrair vazão e head do ponto de interseção
            vazao_bomba, head_value = self.extrair_valores_intersecao(pump, self.system_curve_adjusted)
            
            # Calcular vazão total
            vazao_total = vazao_bomba * n_bombas
            
            # Armazenar os valores calculados para uso posterior
            pump['vazao_bomba'] = vazao_bomba
            pump['vazao_total'] = vazao_total
            pump['head_value'] = head_value
            pump['ponto_intersecao'] = [vazao_bomba, head_value]
            
        except Exception as e:
            logging.error(f"Erro ao calcular ponto de operação: {e}")
            # Valores padrão em caso de erro
            pump['vazao_bomba'] = self.target_flow / n_bombas
            pump['vazao_total'] = self.target_flow
            pump['head_value'] = np.polyval(self.system_curve_adjusted, pump['vazao_bomba'])
            pump['ponto_intersecao'] = [pump['vazao_bomba'], pump['head_value']]
    
    def atualizar_lista_bombas(self):
        """Atualiza a lista de bombas na interface."""
        for pump in self.pumps:
            item_text, tooltip_text = self.formatar_item_lista(pump)
            list_item = QListWidgetItem(item_text)
            list_item.setToolTip(tooltip_text)
            self.list_widget.addItem(list_item)
        
        # Atualizar o estilo da lista
        self.list_widget.setStyleSheet("QListWidget::item:selected { background-color: lightblue; }")
    
    def adjust_system_curve_for_parallel_pumps(self, original_curve, n_bombas):
        """
        Ajusta a curva do sistema para considerar bombas em paralelo.
        
        Parâmetros:
            original_curve: coeficientes da curva do sistema original
            n_bombas: número de bombas em paralelo
            
        Retorna:
            Novos coeficientes para a curva ajustada
        """
        # Determinar um intervalo apropriado para os valores de vazão
        max_flow = getattr(self, 'target_flow', 100.0) * 1.4
        
        # Gerar conjunto de valores de vazão (eixo x)
        x_original = np.linspace(0.001, max_flow, 100)
        
        # Calcular os valores de head correspondentes
        y_original = np.polyval(original_curve, x_original)
        
        # Ajustar os valores de vazão dividindo pelo número de bombas
        x_adjusted = x_original / n_bombas
        
        # Realizar um novo ajuste polinomial de grau 5
        adjusted_curve = np.polyfit(x_adjusted, y_original, 5)
        
        return adjusted_curve
    
    def abrir_curve_input_dialog(self):
        """Abre o diálogo para entrada de pontos da curva da bomba."""
        dialog = CurveInputDialog(self)
        dialog.exec()
    
    def atualizar_plot(self, flow_values, system_head_values_coef, pump_head_coef_values=None, 
                       pump_vazao_min=None, pump_vazao_max=None, intersection_point=None):
        """
        Atualiza o gráfico com as curvas do sistema e da bomba.
        """
        try:
            self.ax.clear()
            
            # Obter o número de bombas em paralelo
            n_bombas = int(self.combo_n_bombas.currentText())
            
            # Plotar a curva do sistema 
            self.plotar_curva_sistema(flow_values, system_head_values_coef, n_bombas)
            
            # Plotar curva da bomba e ponto de interseção
            if pump_head_coef_values is not None and pump_vazao_min is not None and pump_vazao_max is not None:
                self.plotar_curva_bomba(pump_head_coef_values, pump_vazao_min, pump_vazao_max)
                
                # Plotar ponto de interseção
                if intersection_point is not None:
                    self.plotar_ponto_intersecao(intersection_point)
            
            # Configurações do gráfico
            self.configurar_grafico(n_bombas)
            
        except Exception as e:
            logging.error(f"Erro ao atualizar o gráfico: {e}")
    
    def plotar_curva_sistema(self, flow_values, system_head_values_coef, n_bombas):
        """Plota a curva do sistema no gráfico."""
        if system_head_values_coef is None:
            return
            
        # Gerar vazões para o eixo X
        system_flow_values = np.linspace(0.001, max(flow_values) * 1.1, 500)
        
        # Calcular heads para a curva do sistema
        system_head_values = np.polyval(system_head_values_coef, system_flow_values)
        
        # Dividir vazões pelo número de bombas para plotagem
        system_flow_values_ajustado = system_flow_values / n_bombas
        
        # Plotar curva do sistema
        self.ax.plot(system_flow_values_ajustado, system_head_values, 
                    linestyle='-', color='blue', linewidth=2, 
                    label='Curva do Sistema')
    
    def plotar_curva_bomba(self, pump_head_coef_values, pump_vazao_min, pump_vazao_max):
        """Plota a curva da bomba no gráfico."""
        # Gerar valores para curva da bomba
        pump_flow_values = np.linspace(pump_vazao_min, pump_vazao_max, 500)
        pump_head_values = np.polyval(pump_head_coef_values, pump_flow_values)
        
        # Plotar curva da bomba
        self.ax.plot(pump_flow_values, pump_head_values, 
                    linestyle='--', color='green', linewidth=2, 
                    label='Curva da Bomba')
    
    def plotar_ponto_intersecao(self, intersection_point):
        """Plota o ponto de interseção no gráfico."""
        try:
            if isinstance(intersection_point, list) and len(intersection_point) >= 2:
                x, y = intersection_point[0], intersection_point[1]
                
                # Marcar o ponto de interseção no gráfico
                self.ax.plot(x, y, 'ro', markersize=8, label='Ponto de Operação')
                
                # Adicionar linhas tracejadas até os eixos
                self.ax.axhline(y=y, color='r', linestyle=':', alpha=0.5)
                self.ax.axvline(x=x, color='r', linestyle=':', alpha=0.5)
                
                # Adicionar texto com o valor do ponto
                self.ax.annotate(f'({x:.1f}, {y:.1f})', 
                                xy=(x, y), 
                                xytext=(10, 10),
                                textcoords='offset points',
                                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
        except Exception as e:
            logging.error(f"Erro ao plotar ponto de interseção: {e}")
    
    def configurar_grafico(self, n_bombas):
        """Configura as propriedades do gráfico."""
        suffix = 's' if n_bombas > 1 else ''
        
        self.ax.set_xlabel("Vazão por Bomba (m³/h)")
        self.ax.set_ylabel("Head (m)")
        self.ax.set_title(f"Curva do Sistema x Curva da Bomba ({n_bombas} bomba{suffix} em paralelo)")
        self.ax.legend(loc='best')
        self.ax.set_ylim(bottom=0)  # Limite inferior do eixo y para 0
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.canvas.draw()
    
    def on_item_double_clicked(self, item):
        """
        Ao dar duplo clique em um item da lista, atualiza os campos do grupo Dados da Bomba.
        """
        index = self.list_widget.row(item)
        self.selected_pump_index = index
        
        try:
            pump = self.pumps[index]
        except IndexError:
            logging.error("Índice inválido no array de bombas.")
            return

        # Obter dados da bomba
        self.atualizar_dados_bomba_selecionada(pump)
        
        # Atualizar o gráfico
        self.atualizar_grafico_bomba_selecionada(pump)
    
    def atualizar_dados_bomba_selecionada(self, pump):
        """Atualiza os campos de informação da bomba selecionada."""
        # Obter o número de bombas em paralelo
        n_bombas = int(self.combo_n_bombas.currentText())

        # Obter dados da bomba
        vazao_bomba = pump.get('vazao_bomba', 0.0)
        vazao_total = vazao_bomba * n_bombas
        head_value = pump.get('head_value', 0.0)
        
        # Formatação dos números com vírgula como separador decimal
        flow_total_str = f"{vazao_total:.2f}".replace('.', ',')
        flow_bomba_str = f"{vazao_bomba:.2f}".replace('.', ',')
        head_str = f"{head_value:.2f}".replace('.', ',')
        
        eff_str = f"{pump.get('pump_eff', 0):.2f}".replace('.', ',')
        power_per_pump_str = f"{pump.get('pump_power', 0):.2f}".replace('.', ',')
        power_total_str = f"{pump.get('pump_power', 0) * n_bombas:.2f}".replace('.', ',')
        npsh_str = f"{pump.get('pump_npshr', 0):.2f}".replace('.', ',')

        # Atualizar os campos de informação
        self.result_flow.setText(f"{flow_total_str} m³/h total ({flow_bomba_str} m³/h por bomba)")
        self.result_head.setText(head_str + " m")
        self.result_pump.setText(f"{pump.get('marca', 'N/D')} / {pump.get('modelo', 'N/D')}")
        self.result_eff.setText(eff_str + "%")
        self.result_power.setText(f"{power_per_pump_str} cv por bomba ({power_total_str} cv total)")
        self.result_npsh.setText(npsh_str + " m")
        self.result_rotor_diametro.setText(f"{pump.get('diametro', 'N/D')} mm")

        # Calcular e exibir a margem de NPSH
        self.atualizar_margem_npsh(pump)
    
    def atualizar_margem_npsh(self, pump):
        """Atualiza o campo de margem de NPSH e aplica formatação condicional."""
        npsh_disponivel = self.system_input_widget.get_npsh_disponivel()
        npsh_requerido = pump.get('pump_npshr', 0)
        
        if npsh_disponivel is not None:
            margem_npsh = npsh_disponivel - npsh_requerido
            margem_str = f"{margem_npsh:.2f}".replace('.', ',')

            self.result_npsh_comparison.setText(margem_str + " m")
        else:
            self.result_npsh_comparison.setText("N/D")
    
    def atualizar_grafico_bomba_selecionada(self, pump):
        """Atualiza o gráfico com os dados da bomba selecionada."""
        try:
            # Obter parâmetros da bomba
            pump_head_coef_values = pump.get('pump_coef_head')
            pump_vazao_min = pump.get('pump_vazao_min', 0)
            pump_vazao_max = pump.get('pump_vazao_max', 100)
            
            # Usar o ponto de interseção já calculado
            intersection_point = pump.get('ponto_intersecao', [pump.get('vazao_bomba', 0), pump.get('head_value', 0)])
            
            # Atualizar o gráfico
            flow_values = np.linspace(0, max(pump_vazao_max, self.target_flow * 1.4), 500)
            self.atualizar_plot(flow_values, self.system_curve, pump_head_coef_values, 
                            pump_vazao_min, pump_vazao_max, intersection_point)
        except Exception as e:
            logging.error(f"Erro ao atualizar o gráfico da bomba selecionada: {e}")


if __name__ == '__main__':
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    app = QApplication(sys.argv)
    # Widgets dummy para testes
    system_input_widget = QWidget()
    fluid_prop_input_widget = QWidget()
    main_widget = PumpSelectionWidget(system_input_widget, fluid_prop_input_widget)
    main_widget.show()
    sys.exit(app.exec())