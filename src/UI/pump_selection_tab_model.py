import sys
import sqlite3
import json
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt

# Caminho do banco de dados
db_path = "./src/db/pump_data.db"

class PumpSelectionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Bombas")
        self.setGeometry(100, 100, 1200, 700)
        
        # Layout principal
        layout = QVBoxLayout()
        
        # Campos de entrada
        self.model_input = QLineEdit()
        self.rpm_input = QLineEdit()
        self.q_min_input = QLineEdit()
        self.q_max_input = QLineEdit()
        
        # Botão para adicionar bomba
        add_button = QPushButton("Adicionar Bomba")
        add_button.clicked.connect(self.add_pump)
        
        # Dropdown para seleção da bomba
        self.pump_selector = QComboBox()
        self.load_pumps()
        
        # Botão para exibir curva
        show_curve_button = QPushButton("Exibir Curva")
        show_curve_button.clicked.connect(self.plot_curve)
        
        # Gráfico PyQtGraph
        self.plot_widget = pg.PlotWidget()
        
        # Adicionar widgets ao layout
        layout.addWidget(QLabel("Modelo:"))
        layout.addWidget(self.model_input)
        layout.addWidget(QLabel("Rotação (RPM):"))
        layout.addWidget(self.rpm_input)
        layout.addWidget(QLabel("Vazão Mínima (m³/h):"))
        layout.addWidget(self.q_min_input)
        layout.addWidget(QLabel("Vazão Máxima (m³/h):"))
        layout.addWidget(self.q_max_input)
        layout.addWidget(add_button)
        layout.addWidget(QLabel("Selecionar Bomba:"))
        layout.addWidget(self.pump_selector)
        layout.addWidget(show_curve_button)
        layout.addWidget(self.plot_widget)
        
        self.setLayout(layout)
    
    def load_pumps(self):
        """Carrega a lista de bombas disponíveis no banco de dados."""
        self.pump_selector.clear()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT modelo FROM bombas")
        bombas = cursor.fetchall()
        conn.close()
        
        for bomba in bombas:
            self.pump_selector.addItem(bomba[0])
    
    def add_pump(self):
        """Adiciona uma nova bomba ao banco de dados."""
        modelo = self.model_input.text()
        rotacao = self.rpm_input.text()
        q_min = self.q_min_input.text()
        q_max = self.q_max_input.text()
        
        if not (modelo and rotacao and q_min and q_max):
            QMessageBox.warning(self, "Erro", "Preencha todos os campos!")
            return
        
        try:
            rotacao = int(rotacao)
            q_min = float(q_min)
            q_max = float(q_max)
        except ValueError:
            QMessageBox.warning(self, "Erro", "Rotação e vazão devem ser números!")
            return
        
        coef = json.dumps(np.random.uniform(-1, 1, 5).tolist())
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bombas (modelo, rotacao, vazao_min, vazao_max, coef_head, coef_eff, coef_npshr, coef_power)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (modelo, rotacao, q_min, q_max, coef, coef, coef, coef))
        conn.commit()
        conn.close()
        
        QMessageBox.information(self, "Sucesso", "Bomba adicionada com sucesso!")
        self.load_pumps()
    
    def plot_curve(self):
        """Exibe a curva da bomba selecionada."""
        modelo = self.pump_selector.currentText()
        if not modelo:
            QMessageBox.warning(self, "Erro", "Nenhuma bomba selecionada!")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT vazao_min, vazao_max, coef_head FROM bombas WHERE modelo = ?", (modelo,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            q_min, q_max, coef_head = result
            coef_head = json.loads(coef_head)
            vazao = np.linspace(q_min, q_max, 100)
            altura = np.polyval(coef_head, vazao)
            
            self.plot_widget.clear()
            self.plot_widget.plot(vazao, altura, pen='b', name=f"Curva {modelo}")
            self.plot_widget.setLabel('left', "Altura Manométrica (m)")
            self.plot_widget.setLabel('bottom', "Vazão (m³/h)")
            self.plot_widget.setTitle("Curva da Bomba")
        else:
            QMessageBox.warning(self, "Erro", "Dados da bomba não encontrados!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PumpSelectionWidget()
    window.show()
    sys.exit(app.exec())
