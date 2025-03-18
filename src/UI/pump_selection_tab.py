import sys
import os
import sqlite3
import json
import numpy as np
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QTableWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QWidget,
    QFormLayout,
    QPushButton,
    QStyledItemDelegate,
    QGroupBox,
    QListWidget,
    QMessageBox,
    QListWidgetItem,
    QComboBox
)
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from typing import List, Union, Dict, Any
import logging

# Importa a função de cálculo da curva do sistema
from UI.func.pressure_drop.total_head_loss import calculate_pipe_system_head_loss
# Importa a função de seleção automática de bomba
from UI.func.auto_pump_selection import auto_pump_selection
# Importa as funções auxiliares para perdas locais
from UI.extra.local_loss import size_dict_internal_diameter_sch40, size_dict, get_size_singularities_loss_values

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
        
        vertical_layout = QVBoxLayout(self)
        instruction_label = QLabel("Preencha a tabela com os pontos da curva característica da bomba.", self)
        vertical_layout.addWidget(instruction_label)
        
        horizontal_layout = QHBoxLayout()
        vertical_layout.addLayout(horizontal_layout)
        
        pump_info_widget = QWidget(self)
        pump_info_layout = QFormLayout(pump_info_widget)
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
        self.btn_adicionar_bomba = QPushButton("Adicionar Bomba", pump_info_widget)
        pump_info_layout.addRow(self.btn_adicionar_bomba)
        self.btn_adicionar_bomba.clicked.connect(self.adicionar_bomba)
        
        horizontal_layout.addWidget(pump_info_widget)
        
        self.table_widget = QTableWidget(6, 5, self)
        headers = ["Vazão", "Head", "Eficiência", "NPSHr", "Potência"]
        self.table_widget.setHorizontalHeaderLabels(headers)
        self.table_widget.setItemDelegate(FloatDelegate(self.table_widget))
        horizontal_layout.addWidget(self.table_widget)
        
        horizontal_layout.setStretch(0, 3)
        horizontal_layout.setStretch(1, 7)
    
    def adicionar_bomba(self):
        print("Bomba adicionada com sucesso!")

class PumpSelectionWidget(QWidget):
    """
    Janela principal para gerenciar bombas e exibir curvas.
    Neste código, o valor de "Vazão (m³/h)" é utilizado como target_flow.
    """
    def __init__(self, system_input_widget, fluid_prop_input_widget, parent=None):
        super().__init__(parent)
        self.system_input_widget = system_input_widget
        self.fluid_prop_input_widget = fluid_prop_input_widget
        self.system_curve = None
        self.target_flow = None
        self.init_ui()
        self.setup_db_timer()
    
    def init_ui(self):
        self.setWindowTitle("Seleção de Bombas")
        self.resize(800, 600)
        main_layout = QHBoxLayout(self)
        
        # Área Esquerda: inputs, resultados e botões
        left_widget = QWidget(self)
        left_layout = QVBoxLayout(left_widget)
        
        # -- Campo de Vazão (que também será o target_flow) --
        vazao_widget = QWidget(left_widget)
        vazao_layout = QHBoxLayout(vazao_widget)
        vazao_layout.setContentsMargins(0, 0, 0, 0)
        label_vazao = QLabel("Vazão (m³/h):", vazao_widget)
        vazao_layout.addWidget(label_vazao)
        self.line_edit_vazao = QLineEdit(vazao_widget)
        self.line_edit_vazao.setValidator(QDoubleValidator(0.0, 1e9, 2, self))
        self.line_edit_vazao.setPlaceholderText("Informe a vazão")
        vazao_layout.addWidget(self.line_edit_vazao)
        left_layout.addWidget(vazao_widget)
        
        # -- Dropdown para Diâmetro (Bitola) --
        diametro_dropdown_widget = QWidget(left_widget)
        diametro_dropdown_layout = QHBoxLayout(diametro_dropdown_widget)
        diametro_dropdown_layout.setContentsMargins(0, 0, 0, 0)
        label_diametro = QLabel("Diâmetro:", diametro_dropdown_widget)
        diametro_dropdown_layout.addWidget(label_diametro)
        self.combo_diametro_pipe = QComboBox(diametro_dropdown_widget)
        # Preenche o dropdown com as chaves do dict size_dict_internal_diameter_sch40
        self.combo_diametro_pipe.addItems(list(size_dict_internal_diameter_sch40.keys()))
        diametro_dropdown_layout.addWidget(self.combo_diametro_pipe)
        left_layout.addWidget(diametro_dropdown_widget)
        
        # Conecta o sinal do dropdown para atualizar a velocidade
        self.combo_diametro_pipe.currentIndexChanged.connect(self.atualizar_velocidade)
        
        # -- Campo de Velocidade do Fluido (display somente leitura) --
        velocity_widget = QWidget(left_widget)
        velocity_layout = QHBoxLayout(velocity_widget)
        velocity_layout.setContentsMargins(0, 0, 0, 0)
        label_velocity = QLabel("Velocidade (m/s):", velocity_widget)
        velocity_layout.addWidget(label_velocity)
        self.line_edit_velocity = QLineEdit(velocity_widget)
        self.line_edit_velocity.setReadOnly(True)
        self.line_edit_velocity.setPlaceholderText("Será calculada automaticamente")
        velocity_layout.addWidget(self.line_edit_velocity)
        left_layout.addWidget(velocity_widget)
        
        # Conecta alteração da vazão para atualizar a velocidade
        self.line_edit_vazao.textChanged.connect(self.atualizar_velocidade)
        
        # -- QGroupBox: Seleção de Bomba (Lista) --
        self.pump_list_box = QGroupBox("Seleção de Bomba (Lista)", left_widget)
        list_layout = QVBoxLayout(self.pump_list_box)
        self.btn_selecionar_bomba = QPushButton("Selecionar Bomba", self.pump_list_box)
        self.btn_selecionar_bomba.clicked.connect(self.selecionar_bomba)
        list_layout.addWidget(self.btn_selecionar_bomba)
        self.list_widget = QListWidget(self.pump_list_box)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        list_layout.addWidget(self.list_widget)
        left_layout.addWidget(self.pump_list_box)
        
        # -- QGroupBox: Dados da Bomba (resultados) --
        self.pump_data_box = QGroupBox("Dados da Bomba", left_widget)
        data_layout = QFormLayout(self.pump_data_box)

        self.result_flow = QLineEdit()
        self.result_flow.setReadOnly(True)
        data_layout.addRow("Vazão:", self.result_flow)

        self.result_head = QLineEdit()
        self.result_head.setReadOnly(True)
        data_layout.addRow("Head:", self.result_head)

        self.result_pump = QLineEdit()
        self.result_pump.setReadOnly(True)
        data_layout.addRow("Bomba (Marca/Modelo):", self.result_pump)

        # Novo campo para Diâmetro do rotor
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

        left_layout.addWidget(self.pump_data_box)
        left_layout.addStretch()

        
        # Botões finais
        self.btn_adicionar_curva = QPushButton("Adicionar nova curva de bomba", left_widget)
        self.btn_adicionar_curva.clicked.connect(self.abrir_curve_input_dialog)
        left_layout.addWidget(self.btn_adicionar_curva)
        self.btn_calcular = QPushButton("Calcular", left_widget)
        self.btn_calcular.clicked.connect(self.calcular_sistema)
        left_layout.addWidget(self.btn_calcular)
        
        # Área Direita: Gráfico
        right_widget = QWidget(self)
        right_layout = QVBoxLayout(right_widget)
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("Flow (m³/h)")
        self.ax.set_ylabel("Head")
        self.ax.set_title("Pump Characteristic Curve")
        self.canvas.draw()
        right_layout.addWidget(self.canvas)
        
        main_layout.addWidget(left_widget, 3)
        main_layout.addWidget(right_widget, 7)
    
    def setup_db_timer(self):
        """Configura um timer para monitorar alterações no banco de dados."""
        self.last_db_mod_time = os.path.getmtime("./src/db/pump_data.db")
        self.timer = QTimer(self)
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.check_db_update)
        self.timer.start()
    
    def check_db_update(self):
        try:
            current_mod_time = os.path.getmtime("./src/db/pump_data.db")
            if current_mod_time != self.last_db_mod_time:
                self.last_db_mod_time = current_mod_time
                # Atualizações se necessárias
        except Exception as e:
            print("Erro ao verificar atualização do banco de dados:", e)
    
    def atualizar_velocidade(self):
        """
        Calcula e atualiza a velocidade do fluido com base na vazão e no diâmetro selecionado.
        A fórmula utilizada é: v = Q / A, onde Q (m³/s) é a vazão convertida e A = π*(d/2)².
        O diâmetro (d) é obtido a partir do dropdown usando size_dict_internal_diameter_sch40.
        """
        try:
            q_m3_h = float(self.line_edit_vazao.text())
        except ValueError:
            self.line_edit_velocity.setText("")
            return
        # Converte vazão de m³/h para m³/s
        q_m3_s = q_m3_h / 3600.0
        # Obtém o valor selecionado no dropdown
        selected_size = self.combo_diametro_pipe.currentText()  # Debug
        try:
            d = size_dict_internal_diameter_sch40[selected_size]*0.001  # Converte para metros
        except KeyError:
            print("Chave não encontrada para o diâmetro, utilizando valor padrão 0.05 m")
            d = 0.05  # Valor padrão se não encontrado
        area = np.pi * (d / 2) ** 2
        velocity = q_m3_s / area
        self.line_edit_velocity.setText(f"{velocity:.2f}")

        
    def formatar_item_lista(self, pump: Dict[str, Any]) -> tuple[str, str]:
        """
        Formata o texto do item e o tooltip a partir dos dados da bomba.
        """
        # Valor de vazão de operação, com validação do campo 'intersecoes'
        try:
            operacao_vazao = pump['intersecoes'][0][0]
        except (KeyError, IndexError):
            operacao_vazao = 0.0

        item_text = (f"Marca: {pump.get('marca', 'N/D')}, Modelo: {pump.get('modelo', 'N/D')}, "
                     f"Diâmetro: {pump.get('diametro', 'N/D')}, Rotação: {pump.get('rotacao', 'N/D')}, "
                     f"Eff.: {pump.get('pump_eff', 0):.2f}")
        tooltip_text = (f"Vazão: {operacao_vazao:.2f} m³/h\n"
                        f"Rotação: {pump.get('rotacao', 'N/D')} rpm\n"
                        f"NPSHr: {pump.get('pump_npshr', 0):.1f} m\n"
                        f"Potência: {pump.get('pump_power', 0):.1f} cv")
        return item_text, tooltip_text

    def selecionar_bomba(self) -> None:
        """
        Executa o cálculo do sistema, chama auto_pump_selection e atualiza a lista com os resultados.
        O target_flow é obtido a partir do campo de vazão.
        Ordena as bombas pela proximidade do ponto de operação (vazão de interseção) com o target_flow.
        """
        self.system_curve, self.target_flow = self.calcular_sistema()
        if self.system_curve is None or self.target_flow is None:
            logging.error("Parâmetros do sistema não definidos.")
            return

        pumps = auto_pump_selection(self.system_curve, self.target_flow)
        logging.info(f"Bombas selecionadas: {pumps}")
        self.list_widget.clear()

        if isinstance(pumps, str):
            self.list_widget.addItem(pumps)
            self.pumps = []
        elif pumps:
            # Ordena as bombas pela proximidade do ponto de interseção com o target_flow,
            # garantindo que a bomba com a vazão de operação mais próxima do target apareça primeiro.
            try:
                pumps_sorted = sorted(
                    pumps,
                    key=lambda p: abs(p.get('intersecoes', [[self.target_flow]])[0][0] - self.target_flow)
                )
            except Exception as e:
                logging.error(f"Erro ao ordenar bombas: {e}")
                pumps_sorted = pumps

            self.pumps = pumps_sorted
            for pump in self.pumps:
                item_text, tooltip_text = self.formatar_item_lista(pump)
                list_item = QListWidgetItem(item_text)
                list_item.setToolTip(tooltip_text)
                self.list_widget.addItem(list_item)
            self.list_widget.setStyleSheet("QListWidget::item:selected { background-color: lightblue; }")
        else:
            self.list_widget.addItem("Nenhuma bomba encontrada.")


    
    def abrir_curve_input_dialog(self):
        dialog = CurveInputDialog(self)
        dialog.exec()
    
    def atualizar_plot(self, flow_values, system_head_values_coef, pump_head_coef_values=None, pump_vazao_min=None, pump_vazao_max=None, intersection_point=None):
        self.ax.clear()
        system_head_values = np.polyval(system_head_values_coef, flow_values)
        self.ax.plot(flow_values, system_head_values, linestyle='-', label='Curva do Sistema')
        if pump_head_coef_values is not None:
            pump_flow_values = np.linspace(pump_vazao_min, pump_vazao_max, 500)
            pump_head_values = np.polyval(pump_head_coef_values, pump_flow_values)
            self.ax.plot(pump_flow_values, pump_head_values, linestyle='--', label='Curva da Bomba')
            if intersection_point is not None:
                self.ax.plot(intersection_point[0], intersection_point[1], 'ro', label='Intersecção')
        self.ax.set_xlabel("Flow (m³/h)")
        self.ax.set_ylabel("Head")
        self.ax.set_title("Curva do Sistema x Curva da Bomba")
        self.ax.legend()
            # Configura o limite inferior do eixo y para 0
        self.ax.set_ylim(bottom=0)
        self.canvas.draw()
    
    def calcular_sistema(self):
        """
        Executa o cálculo do sistema utilizando os valores dos widgets injetados,
        plota o ajuste polinomial e retorna os parâmetros (system_curve e target_flow)
        para a seleção automática de bomba.
        O target_flow é obtido a partir do campo de vazão.
        """

        
        spinbox_suction = self.system_input_widget.get_spinbox_values_suction()
        suction_size = self.combo_diametro_pipe.currentText()
        spinbox_discharge = self.system_input_widget.get_spinbox_values_discharge()
        discharge_size = self.combo_diametro_pipe.currentText()
        mu_value = self.fluid_prop_input_widget.get_mu_input_value()
        rho_value = self.fluid_prop_input_widget.get_rho_input_value()
        print(spinbox_suction, suction_size, spinbox_discharge, discharge_size, mu_value, rho_value)
        
        target_flow = self.get_target_flow()
        if target_flow is None:
            return None, None
        
        head_values_coef, min_flow, max_flow = calculate_pipe_system_head_loss(
            spinbox_suction, suction_size,
            spinbox_discharge, discharge_size,
            target_flow, mu_value, rho_value
        )
        
        flow_values = np.linspace(min_flow, max_flow, 500)
        self.flow_values = flow_values
        self.atualizar_plot(flow_values, head_values_coef)
        print("O cálculo do sistema foi feito com ajuste polinomial (linha contínua)!")
        
        self.system_curve = head_values_coef
        self.target_flow = target_flow
        return head_values_coef, target_flow
        
    def get_target_flow(self):
        try:
            # Utiliza o valor da vazão como target_flow
            return float(self.line_edit_vazao.text())
        except ValueError:
            QMessageBox.critical(self, "Erro", "Insira o valor da Vazão corretamente!")
            return None
    
    def on_item_double_clicked(self, item):
        """
        Ao dar duplo clique em um item da lista, atualiza os campos do grupo Dados da Bomba.
        """
        index = self.list_widget.row(item)
        try:
            pump = self.pumps[index]
        except IndexError:
            print("Índice inválido no array de bombas.")
            return

        # Formatação dos números com vírgula como separador decimal
        flow_str = f"{pump['intersecoes'][0][0]:.2f}".replace('.', ',')
        head_value = np.polyval(self.system_curve, pump['intersecoes'][0][0])
        head_str = f"{head_value:.2f}".replace('.', ',')
        eff_str = f"{pump['pump_eff']:.2f}".replace('.', ',')
        power_str = f"{pump['pump_power']:.2f}".replace('.', ',')
        npsh_str = f"{pump['pump_npshr']:.2f}".replace('.', ',')

        self.result_flow.setText(flow_str + " m³/h")
        self.result_head.setText(head_str)
        self.result_pump.setText(f"{pump['marca']} / {pump['modelo']}")
        self.result_eff.setText(eff_str + "%")
        self.result_power.setText(power_str + " cv")
        self.result_npsh.setText(npsh_str + " m")
        
        # Atualiza o novo campo com o diâmetro do rotor
        self.result_rotor_diametro.setText(pump['diametro'])

        # Exibe os dados da bomba selecionada no console
        print(f"Selecionada Bomba -> Marca: {pump['marca']}, Modelo: {pump['modelo']}, "
            f"Diâmetro: {pump['diametro']}, Rotação: {pump['rotacao']}")

        pump_head_coef_values = pump.get('pump_coef_head')
        intersection_points = pump.get('intersecoes')
        pump_vazao_min = pump.get('pump_vazao_min')
        pump_vazao_max = pump.get('pump_vazao_max')
        pump_flow_values = np.linspace(pump_vazao_min, pump_vazao_max, 500)
        # Atualiza o gráfico com a curva do sistema e a curva da bomba (e o(s) ponto(s) de interseção, se disponível)
        self.atualizar_plot(pump_flow_values, self.system_curve, pump_head_coef_values, pump_vazao_min, pump_vazao_max, intersection_points)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Widgets dummy para injeção; substitua pelos reais conforme necessário
    system_input_widget = QWidget()
    fluid_prop_input_widget = QWidget()
    main_widget = PumpSelectionWidget(system_input_widget, fluid_prop_input_widget)
    main_widget.show()
    sys.exit(app.exec())
