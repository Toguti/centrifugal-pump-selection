# pump_selection_tab.py

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
    QComboBox,
    QListWidget,
    QMessageBox,
    QListWidgetItem
)
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# Importa a função de cálculo da curva do sistema
from UI.func.pressure_drop.total_head_loss import calculate_pipe_system_head_loss
# Importa a função de seleção automática de bomba
from UI.func.auto_pump_selection import auto_pump_selection

# Caminho do banco de dados
DB_PATH = "./src/db/pump_data.db"

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
    Todas as funcionalidades de seleção de bomba (por filtros e por lista)
    foram integradas nesta classe.
    """
    def __init__(self, system_input_widget, fluid_prop_input_widget, parent=None):
        super().__init__(parent)
        self.system_input_widget = system_input_widget
        self.fluid_prop_input_widget = fluid_prop_input_widget
        # Para a seleção automática, esses atributos serão definidos após o cálculo do sistema
        self.system_curve = None
        self.target_flow = None
        self.init_ui()
        self.setup_db_timer()
    
    def init_ui(self):
        self.setWindowTitle("Seleção de Bombas")
        self.resize(800, 600)
        main_layout = QHBoxLayout(self)
        
        # Área Esquerda: inputs, seleção de bomba e botões
        left_widget = QWidget(self)
        left_layout = QVBoxLayout(left_widget)
        
        # Widget de Vazão
        vazao_widget = QWidget(left_widget)
        vazao_layout = QHBoxLayout(vazao_widget)
        vazao_layout.setContentsMargins(0, 0, 0, 0)
        label_vazao = QLabel("Vazão:", vazao_widget)
        vazao_layout.addWidget(label_vazao)
        self.line_edit_vazao = QLineEdit(vazao_widget)
        self.line_edit_vazao.setValidator(QDoubleValidator(0.0, 1e9, 2, self))
        self.line_edit_vazao.setPlaceholderText("Valor em m³/h")
        vazao_layout.addWidget(self.line_edit_vazao)
        left_layout.addWidget(vazao_widget)
        
        # QGroupBox: Seleção de Bomba (Lista)
        self.pump_list_box = QGroupBox("Seleção de Bomba (Lista)", left_widget)
        list_layout = QVBoxLayout(self.pump_list_box)
        # Botão "Selecionar Bomba" acima da lista
        self.btn_selecionar_bomba = QPushButton("Selecionar Bomba", self.pump_list_box)
        self.btn_selecionar_bomba.clicked.connect(self.selecionar_bomba)
        list_layout.addWidget(self.btn_selecionar_bomba)
        self.list_widget = QListWidget(self.pump_list_box)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        list_layout.addWidget(self.list_widget)
        left_layout.addWidget(self.pump_list_box)
        
        # QGroupBox: Seleção de Bomba (Filtros)
        self.pump_filter_box = QGroupBox("Seleção de Bomba (Filtros)", left_widget)
        filter_layout = QFormLayout(self.pump_filter_box)
        # Cria os QComboBox para os filtros
        self.combo_marca = QComboBox(self)
        self.combo_modelo = QComboBox(self)
        self.combo_diametro = QComboBox(self)
        self.combo_rotacao = QComboBox(self)
        # Item neutro "Selecione"
        self.combo_marca.addItem("Selecione")
        self.combo_modelo.addItem("Selecione")
        self.combo_diametro.addItem("Selecione")
        self.combo_rotacao.addItem("Selecione")
        filter_layout.addRow("Marca:", self.combo_marca)
        filter_layout.addRow("Modelo:", self.combo_modelo)
        # Botão "Mostrar Gráfico da Bomba" logo abaixo do modelo
        filter_layout.addRow("Diametro:", self.combo_diametro)
        filter_layout.addRow("Rotação:", self.combo_rotacao)
        self.btn_mostrar_grafico = QPushButton("Mostrar Gráfico da Bomba", self)
        filter_layout.addRow("", self.btn_mostrar_grafico)
        left_layout.addWidget(self.pump_filter_box)
        
        # Conecta os sinais dos QComboBox para atualização encadeada
        self.combo_marca.currentIndexChanged.connect(self.on_marca_changed)
        self.combo_modelo.currentIndexChanged.connect(self.on_modelo_changed)
        self.combo_diametro.currentIndexChanged.connect(self.on_diametro_changed)
        # Conecta o botão "Mostrar Gráfico da Bomba" (placeholder)
        self.btn_mostrar_grafico.clicked.connect(self.mostrar_grafico_bomba)
        
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
        
        # Carrega dados iniciais nos filtros
        self.load_marcas()
    
    def setup_db_timer(self):
        """Configura um timer para monitorar alterações no banco de dados."""
        self.last_db_mod_time = os.path.getmtime(DB_PATH)
        self.timer = QTimer(self)
        self.timer.setInterval(2000)  # a cada 2 segundos
        self.timer.timeout.connect(self.check_db_update)
        self.timer.start()
    
    # --- Funções de acesso ao banco de dados (antes no pump_db_selection.py) ---
    def get_db_connection(self):
        return sqlite3.connect(DB_PATH)
    
    def load_marcas(self):
        self.combo_marca.blockSignals(True)
        self.combo_marca.clear()
        self.combo_marca.addItem("Selecione")
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT marca FROM pump_models ORDER BY marca;")
            for row in cursor.fetchall():
                self.combo_marca.addItem(str(row[0]))
        except Exception as e:
            print("Erro ao carregar marcas:", e)
        finally:
            conn.close()
        self.combo_marca.blockSignals(False)
        self.reset_combo(self.combo_modelo)
        self.reset_combo(self.combo_diametro)
        self.reset_combo(self.combo_rotacao)
        self.combo_modelo.setEnabled(False)
        self.combo_diametro.setEnabled(False)
        self.combo_rotacao.setEnabled(False)
    
    def on_marca_changed(self, index):
        marca = self.combo_marca.currentText()
        if marca != "Selecione":
            self.load_modelos(marca)
            self.combo_modelo.setEnabled(True)
        else:
            self.reset_combo(self.combo_modelo)
            self.reset_combo(self.combo_diametro)
            self.reset_combo(self.combo_rotacao)
            self.combo_modelo.setEnabled(False)
            self.combo_diametro.setEnabled(False)
            self.combo_rotacao.setEnabled(False)
    
    def load_modelos(self, marca):
        self.combo_modelo.blockSignals(True)
        self.combo_modelo.clear()
        self.combo_modelo.addItem("Selecione")
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT modelo FROM pump_models WHERE marca = ? ORDER BY modelo;", (marca,))
            for row in cursor.fetchall():
                self.combo_modelo.addItem(str(row[0]))
        except Exception as e:
            print("Erro ao carregar modelos:", e)
        finally:
            conn.close()
        self.combo_modelo.blockSignals(False)
        self.reset_combo(self.combo_diametro)
        self.reset_combo(self.combo_rotacao)
        self.combo_diametro.setEnabled(False)
        self.combo_rotacao.setEnabled(False)
    
    def on_modelo_changed(self, index):
        modelo = self.combo_modelo.currentText()
        if modelo != "Selecione":
            self.load_diametros(modelo)
            self.combo_diametro.setEnabled(True)
        else:
            self.reset_combo(self.combo_diametro)
            self.reset_combo(self.combo_rotacao)
            self.combo_diametro.setEnabled(False)
            self.combo_rotacao.setEnabled(False)
    
    def load_diametros(self, modelo):
        self.combo_diametro.blockSignals(True)
        self.combo_diametro.clear()
        self.combo_diametro.addItem("Selecione")
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT diametro FROM pump_models WHERE modelo = ? ORDER BY diametro;", (modelo,))
            for row in cursor.fetchall():
                self.combo_diametro.addItem(str(row[0]))
        except Exception as e:
            print("Erro ao carregar diametros:", e)
        finally:
            conn.close()
        self.combo_diametro.blockSignals(False)
        self.reset_combo(self.combo_rotacao)
        self.combo_rotacao.setEnabled(False)
    
    def on_diametro_changed(self, index):
        diametro = self.combo_diametro.currentText()
        if diametro != "Selecione":
            self.load_rotacoes(diametro)
            self.combo_rotacao.setEnabled(True)
        else:
            self.reset_combo(self.combo_rotacao)
            self.combo_rotacao.setEnabled(False)
    
    def load_rotacoes(self, diametro):
        self.combo_rotacao.blockSignals(True)
        self.combo_rotacao.clear()
        self.combo_rotacao.addItem("Selecione")
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT rotacao FROM pump_models WHERE diametro = ? ORDER BY rotacao;", (diametro,))
            for row in cursor.fetchall():
                self.combo_rotacao.addItem(str(row[0]))
        except Exception as e:
            print("Erro ao carregar rotações:", e)
        finally:
            conn.close()
        self.combo_rotacao.blockSignals(False)
    
    def reset_combo(self, combo):
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("Selecione")
        combo.blockSignals(False)
    
    def check_db_update(self):
        try:
            current_mod_time = os.path.getmtime(DB_PATH)
            if current_mod_time != self.last_db_mod_time:
                self.last_db_mod_time = current_mod_time
                self.reload_all()
        except Exception as e:
            print("Erro ao verificar atualização do banco de dados:", e)
    
    def reload_all(self):
        self.load_marcas()
    
    def mostrar_grafico_bomba(self):
        # Placeholder: aqui você pode implementar a exibição do gráfico da bomba selecionada
        print("Mostrar gráfico da bomba (placeholder).")
    
    # --- Funções para seleção automática de bomba via lista ---
    def selecionar_bomba(self):
        """
        Método chamado pelo botão "Selecionar Bomba" do grupo de lista.
        Utiliza os parâmetros do sistema (system_curve e target_flow) para chamar a função
        auto_pump_selection, ordena as bombas por eficiência (maior para menor) e atualiza o QListWidget
        com os resultados. Cada item da lista possui um tooltip com informações adicionais e
        feedback visual ao ser selecionado.
        """
        self.system_curve, self.target_flow = self.calcular_sistema()
        if self.system_curve is None or self.target_flow is None:
            print("Parâmetros do sistema não definidos.")
            return

        pumps = auto_pump_selection(self.system_curve, self.target_flow)
        print(pumps)

        self.list_widget.clear()

        if isinstance(pumps, str):
            self.list_widget.addItem(pumps)
            self.pumps = []  # Garante que self.pumps seja uma lista vazia
        elif pumps:
            # Ordena as bombas por eficiência (pump_eff) de forma decrescente
            pumps_sorted = sorted(pumps, key=lambda p: p.get('pump_eff', 0), reverse=True)
            self.pumps = pumps_sorted  # Atualiza o atributo self.pumps com a lista ordenada

            for pump in self.pumps:
                item_text = (f"Marca: {pump['marca']}, Modelo: {pump['modelo']}, "
                            f"Diâmetro: {pump['diametro']}, Rotação: {pump['rotacao']}, "
                            f"Eff.: {pump['pump_eff']:.2f}")
                list_item = QListWidgetItem(item_text)
                # Configura o tooltip com informações adicionais:
                # Inclui Rotação, NPSHr, Potência e o ponto de interseção de vazão (fluxo)
                tooltip_text = (
                    f"Vazão: {pump['intersecoes'][0][0]:.2f}m³/h\n"
                    f"Rotação: {pump['rotacao']}rpm\n"
                    f"NPSHr: {pump['pump_npshr']:.1f}m\n"
                    f"Potência: {pump['pump_power']:.1f}cv"
                )
                list_item.setToolTip(tooltip_text)
                self.list_widget.addItem(list_item)

            # Define feedback visual: muda a cor de fundo do item selecionado
            self.list_widget.setStyleSheet("QListWidget::item:selected { background-color: lightblue; }")
        else:
            self.list_widget.addItem("Nenhuma bomba encontrada.")


    
    def set_system_curve(self, system_curve, target_flow):
        """
        Define os parâmetros necessários para a seleção automática de bomba:
         - system_curve: coeficientes da curva do sistema (polinômio de grau 5)
         - target_flow: fluxo alvo (valor máximo), normalmente obtido do cálculo em PumpSelectionWidget
        """
        self.system_curve = system_curve
        self.target_flow = target_flow

    # --- Outras funções do PumpSelectionWidget ---
    def abrir_curve_input_dialog(self):
        dialog = CurveInputDialog(self)
        dialog.exec()
    
    def atualizar_plot(self, flow_values, system_head_values_coef, pump_head_coef_values=None, pump_vazao_min = None, pump_vazao_max = None, intersection_point=None):
        """
        Atualiza o plot com as curvas fornecidas.

        Parâmetros:
            flow_values (array): Valores de fluxo (eixo X) para o plot.
            system_head_values_coef (array): Coeficientes da curva do sistema.
            pump_head_coef_values (array, opcional): Coeficientes da curva da bomba.
            intersection_point (tuple, opcional): Ponto de intersecção (x, y) entre as curvas,
                                                fornecido somente se ambos os coeficientes forem passados.

        Se os coeficientes da bomba forem fornecidos, plota as duas curvas e, se disponível, o ponto de intersecção.
        Caso contrário, plota somente a curva do sistema.
        """
        self.ax.clear()
        
        # Plota a curva do sistema
        system_head_values = np.polyval(system_head_values_coef, flow_values)
        self.ax.plot(flow_values, system_head_values, linestyle='-', label='Curva do Sistema')
        
        # Verifica se os coeficientes da bomba foram passados para plotagem
        if pump_head_coef_values is not None:
            pump_flow_value = np.linspace(pump_vazao_min, pump_vazao_max, 500)
            pump_head_values = np.polyval(pump_head_coef_values, pump_flow_value)
            self.ax.plot(pump_flow_value, pump_head_values, linestyle='--', label='Curva da Bomba')
            # Se o ponto de intersecção também foi passado, plota-o
            if intersection_point is not None:
                self.ax.plot(intersection_point[0], intersection_point[1], 'ro', label='Intersecção')
        
        self.ax.set_xlabel("Flow (m³/h)")
        self.ax.set_ylabel("Head")
        self.ax.set_title("Curva do Sistema x Curva da Bomba")
        self.ax.legend()
        self.canvas.draw()

    def calcular_sistema(self):
        """
        Executa o cálculo do sistema utilizando os valores dos widgets injetados,
        plota o ajuste polinomial como linha contínua e retorna os parâmetros necessários
        para a seleção automática de bomba.
        """
        # Extrai os valores dos widgets de entrada (métodos do system_input_widget e fluid_prop_input_widget)
        spinbox_suction = self.system_input_widget.get_spinbox_values_suction()
        suction_size = self.system_input_widget.get_suction_size()
        spinbox_discharge = self.system_input_widget.get_spinbox_values_discharge()
        discharge_size = self.system_input_widget.get_discharge_size()
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
        
        # Cria os valores de fluxo e armazena em self.flow_values para uso futuro
        flow_values = np.linspace(min_flow, max_flow, 500)
        self.flow_values = flow_values
        
        # Atualiza o plot chamando a função separada, passando somente a curva do sistema
        self.atualizar_plot(flow_values, head_values_coef)
        
        print("O cálculo do sistema foi feito com ajuste polinomial (linha contínua)!")
        
        # Define os parâmetros no grupo de seleção por lista
        self.set_system_curve(head_values_coef, target_flow)
        return head_values_coef, target_flow
        
    def get_target_flow(self):
        try:
            return float(self.line_edit_vazao.text())
        except ValueError:
            QMessageBox.critical(self, "Erro", "Insira o valor da vazão desejada corretamente!")
            return None

    def on_item_double_clicked(self, item):
        """
        Função acionada ao dar duplo clique em um item da lista de seleção de bomba.
        Recupera o índice do item clicado, obtém o dicionário correspondente em self.pumps e chama
        atualizar_plot, passando:
        - self.flow_values (eixo X)
        - self.system_curve (coeficientes da curva do sistema)
        - pump['pump_coef_head'] (coeficiente da curva da bomba)
        - pump['intersecoes'] (ponto(s) de interseção)
        """
        index = self.list_widget.row(item)
        try:
            pump = self.pumps[index]
        except IndexError:
            print("Índice inválido no array de bombas.")
            return

        # Exibe os dados da bomba selecionada
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
