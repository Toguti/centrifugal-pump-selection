import sys
import sqlite3
import json
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QMessageBox, QDialog, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

# Caminho do banco de dados
db_path = "./src/db/pump_data.db"

class CurveInputDialog(QDialog):
    """Janela para entrada de pontos da curva da bomba."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Curva da Bomba")
        self.setGeometry(200, 200, 300, 200)
        
        self.layout = QFormLayout()
        self.vazao_inputs = [QLineEdit() for _ in range(4)]
        self.head_inputs = [QLineEdit() for _ in range(4)]
        
        for i in range(4):
            self.layout.addRow(f"Vazão {i+1} (m³/h):", self.vazao_inputs[i])
            self.layout.addRow(f"Head {i+1} (m):", self.head_inputs[i])
        
        self.confirm_button = QPushButton("Gerar Curva")
        self.confirm_button.clicked.connect(self.generate_curve)
        self.layout.addWidget(self.confirm_button)
        
        self.setLayout(self.layout)
    
    def generate_curve(self):
        try:
            vazoes = [float(input.text()) for input in self.vazao_inputs]
            heads = [float(input.text()) for input in self.head_inputs]
            self.result = json.dumps(np.polyfit(vazoes, heads, 5).tolist())
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos corretamente com valores numéricos!")

class PumpSelectionWidget(QWidget):
    """Janela principal para gerenciar bombas e exibir curvas."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Bombas")
        self.setGeometry(100, 100, 600, 400)
        self.curve_data = None
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface gráfica."""
        layout = QVBoxLayout()
        
        self.model_input = QLineEdit()
        self.rpm_input = QLineEdit()
        self.q_min_input = QLineEdit()
        self.q_max_input = QLineEdit()
        
        self.add_curve_button = QPushButton("Adicionar Curva da Bomba")
        self.add_curve_button.clicked.connect(self.open_curve_input)
        
        self.add_pump_button = QPushButton("Adicionar Bomba")
        self.add_pump_button.clicked.connect(self.add_pump)
        
        self.pump_selector = QComboBox()
        self.load_pumps()
        
        self.show_curve_button = QPushButton("Exibir Curva")
        self.show_curve_button.clicked.connect(self.plot_curve)
        
        self.chart = QChart()
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(self.chart_view.renderHints())
        
        self.axis_x = QValueAxis()
        self.axis_x.setTitleText("Vazão (m³/h)")
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Altura Manométrica (m)")
        
        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        
        layout.addWidget(QLabel("Modelo:"))
        layout.addWidget(self.model_input)
        layout.addWidget(QLabel("Rotação (RPM):"))
        layout.addWidget(self.rpm_input)
        layout.addWidget(QLabel("Vazão Mínima (m³/h):"))
        layout.addWidget(self.q_min_input)
        layout.addWidget(QLabel("Vazão Máxima (m³/h):"))
        layout.addWidget(self.q_max_input)
        layout.addWidget(self.add_curve_button)
        layout.addWidget(self.add_pump_button)
        layout.addWidget(QLabel("Selecionar Bomba:"))
        layout.addWidget(self.pump_selector)
        layout.addWidget(self.show_curve_button)
        layout.addWidget(self.chart_view)
        
        self.setLayout(layout)
    
    def open_curve_input(self):
        """Abre a janela de entrada de curva da bomba."""
        dialog = CurveInputDialog(self)
        if dialog.exec():
            self.curve_data = dialog.result
    
    def load_pumps(self):
        """Carrega as pump_data disponíveis no banco de dados."""
        self.pump_selector.clear()
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT modelo FROM pump_models")
            for bomba in cursor.fetchall():
                self.pump_selector.addItem(bomba[0])
    
    def add_pump(self):
        """Adiciona uma nova bomba ao banco de dados."""
        modelo = self.model_input.text()
        rotacao = self.rpm_input.text()
        q_min = self.q_min_input.text()
        q_max = self.q_max_input.text()
        
        if not (modelo and rotacao and q_min and q_max and self.curve_data):
            QMessageBox.warning(self, "Erro", "Preencha todos os campos corretamente e adicione uma curva!")
            return
        
        try:
            rotacao = int(rotacao)
            q_min = float(q_min)
            q_max = float(q_max)
        except ValueError:
            QMessageBox.warning(self, "Erro", "Os valores de rotação e vazão devem ser numéricos!")
            return
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pump_data (modelo, rotacao, vazao_min, vazao_max, coef_head, coef_eff, coef_npshr, coef_power)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (modelo, rotacao, q_min, q_max, self.curve_data, self.curve_data, self.curve_data, self.curve_data))
        
        QMessageBox.information(self, "Sucesso", "Bomba adicionada com sucesso!")
        self.load_pumps()
    
    def plot_curve(self):
        """Exibe a curva da bomba selecionada."""
        QMessageBox.information(self, "Info", "Funcionalidade de exibir curva ainda não implementada.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PumpSelectionWidget()
    window.show()
    sys.exit(app.exec())
