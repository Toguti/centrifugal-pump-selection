import sys
import numpy as np
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
    QStyledItemDelegate
)
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
        
        # Layout vertical principal
        vertical_layout = QVBoxLayout(self)
        
        # Label de instrução acima da área de dados
        instruction_label = QLabel("Preencha a tabela com os pontos da curva característica da bomba.", self)
        vertical_layout.addWidget(instruction_label)
        
        # Layout horizontal para agrupar o formulário e a tabela
        horizontal_layout = QHBoxLayout()
        vertical_layout.addLayout(horizontal_layout)
        
        # Widget de formulário para os dados da bomba (lado esquerdo)
        pump_info_widget = QWidget(self)
        pump_info_layout = QFormLayout(pump_info_widget)
        
        # Linha de entrada para "Marca"
        self.line_edit_marca = QLineEdit(pump_info_widget)
        pump_info_layout.addRow("Marca:", self.line_edit_marca)
        
        # Linha de entrada para "Modelo"
        self.line_edit_modelo = QLineEdit(pump_info_widget)
        pump_info_layout.addRow("Modelo:", self.line_edit_modelo)
        
        # Linha de entrada para "Diâmetro" com validação para inteiro
        self.line_edit_diametro = QLineEdit(pump_info_widget)
        self.line_edit_diametro.setValidator(QIntValidator(0, 1000000, self))
        pump_info_layout.addRow("Diâmetro:", self.line_edit_diametro)
        
        # Linha de entrada para "Rotação" com validação para inteiro
        self.line_edit_rotacao = QLineEdit(pump_info_widget)
        self.line_edit_rotacao.setValidator(QIntValidator(0, 1000000, self))
        pump_info_layout.addRow("Rotação:", self.line_edit_rotacao)
        
        # Botão "Adicionar Bomba" logo após o campo de rotação
        self.btn_adicionar_bomba = QPushButton("Adicionar Bomba", pump_info_widget)
        pump_info_layout.addRow(self.btn_adicionar_bomba)
        self.btn_adicionar_bomba.clicked.connect(self.adicionar_bomba)
        
        # Adiciona o formulário (lado esquerdo) no layout horizontal
        horizontal_layout.addWidget(pump_info_widget)
        
        # Cria a tabela removendo as colunas "Marca", "Modelo", "Diâmetro" e "Rotação"
        # A tabela terá 6 linhas e 5 colunas
        self.table_widget = QTableWidget(6, 5, self)
        headers = ["Vazão", "Head", "Eficiência", "NPSHr", "Potência"]
        self.table_widget.setHorizontalHeaderLabels(headers)
        
        # Define um delegate para garantir que os dados inseridos sejam float
        self.table_widget.setItemDelegate(FloatDelegate(self.table_widget))
        
        # Adiciona a tabela (lado direito) no layout horizontal
        horizontal_layout.addWidget(self.table_widget)
        
        # Define a proporção de espaço: esquerda (formulário) 30% e direita (tabela) 70%
        horizontal_layout.setStretch(0, 3)
        horizontal_layout.setStretch(1, 7)
        
    def adicionar_bomba(self):
        print("Bomba adicionada com sucesso!")

class PumpSelectionWidget(QWidget):
    """Janela principal para gerenciar bombas e exibir curvas."""
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface gráfica."""
        self.setWindowTitle("Seleção de Bombas")
        self.resize(800, 600)
        
        # Layout horizontal principal para separar as áreas esquerda e direita
        main_layout = QHBoxLayout(self)
        
        # ---------------------------
        # Área Esquerda (Inputs e Botões)
        # ---------------------------
        left_widget = QWidget(self)
        left_layout = QVBoxLayout(left_widget)
        
        # Widget de Vazão (QLabel + QLineEdit com sufixo 'm³/h')
        vazao_widget = QWidget(left_widget)
        vazao_layout = QHBoxLayout(vazao_widget)
        vazao_layout.setContentsMargins(0, 0, 0, 0)  # Remover margens para "colar" os widgets
        label_vazao = QLabel("Vazão:", vazao_widget)
        vazao_layout.addWidget(label_vazao)
        self.line_edit_vazao = QLineEdit(vazao_widget)
        self.line_edit_vazao.setValidator(QDoubleValidator(0.0, 1e9, 2, self))
        self.line_edit_vazao.setPlaceholderText("Valor em m³/h")
        vazao_layout.addWidget(self.line_edit_vazao)
        
        # Adiciona o widget de vazão no topo do left_layout
        left_layout.addWidget(vazao_widget)
        
        # Adiciona um espaçador para empurrar os botões para a parte inferior
        left_layout.addStretch()
        
        # Botão para abrir a janela de Curva da Bomba (texto alterado)
        self.btn_adicionar_curva = QPushButton("Adicionar nova curva de bomba", left_widget)
        self.btn_adicionar_curva.clicked.connect(self.abrir_curve_input_dialog)
        left_layout.addWidget(self.btn_adicionar_curva)
        
        # Botão "Calcular" abaixo do botão anterior
        self.btn_calcular = QPushButton("Calcular", left_widget)
        self.btn_calcular.clicked.connect(self.calcular_sistema)
        left_layout.addWidget(self.btn_calcular)
        
        # ---------------------------
        # Área Direita (Exibição do Gráfico)
        # ---------------------------
        right_widget = QWidget(self)
        right_layout = QVBoxLayout(right_widget)
        
        # Criação do canvas para exibição do gráfico usando matplotlib
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        # Cria um eixo para o gráfico
        self.ax = self.figure.add_subplot(111)
        # Plot inicial em branco
        self.ax.set_xlabel("Flow (m³/h)")
        self.ax.set_ylabel("Head")
        self.ax.set_title("Pump Characteristic Curve")
        self.canvas.draw()
        right_layout.addWidget(self.canvas)
        
        # Adiciona os widgets esquerdo e direito ao layout principal com proporções 30% e 70%
        main_layout.addWidget(left_widget, 3)
        main_layout.addWidget(right_widget, 7)
    
    def abrir_curve_input_dialog(self):
        """Instancia e abre a janela de entrada da curva da bomba."""
        dialog = CurveInputDialog(self)
        dialog.exec()
    
    def calcular_sistema(self):
        """Função executada ao clicar no botão 'Calcular'."""
        # Chama a função que simula o cálculo do sistema e retorna os pontos do gráfico
        flow, head = self.calculate_pipe_system_head_loss()
        
        # Atualiza o gráfico com os pontos retornados
        self.ax.clear()
        self.ax.plot(flow, head, marker='o', linestyle='-')
        self.ax.set_xlabel("Flow (m³/h)")
        self.ax.set_ylabel("Head")
        self.ax.set_title("Pump Characteristic Curve")
        self.canvas.draw()
        
        print("O Cálculo do sistema foi feito!")
    
    def calculate_pipe_system_head_loss(self):
        """
        Função que simula o cálculo da perda de carga no sistema,
        retornando arrays de 'flow' e 'head' para o gráfico.
        """
        # Exemplo: gera 20 pontos de fluxo entre 0 e 100 m³/h
        flow = np.linspace(0, 100, 20)
        # Exemplo: Head decresce linearmente em função do fluxo
        head = 100 - 0.5 * flow
        return flow, head

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_widget = PumpSelectionWidget()
    main_widget.show()
    sys.exit(app.exec())