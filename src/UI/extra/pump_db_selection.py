# pump_db_selection.py

import os
import sqlite3
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QGroupBox, QFormLayout, QComboBox, QVBoxLayout, QPushButton, QListWidget
# Importa a função de seleção automática de bomba
from UI.func.auto_pump_selection import auto_pump_selection

DB_PATH = "./src/db/pump_data.db"

class PumpDBSelectionWidget(QGroupBox):
    """Widget para seleção de bomba com filtros provenientes do banco de dados SQLite."""
    def __init__(self, parent=None):
        super().__init__("Seleção de Bomba (Filtros)", parent)
        self.layout = QFormLayout(self)
        
        # Cria os QComboBox para cada parâmetro
        self.combo_marca = QComboBox(self)
        self.combo_modelo = QComboBox(self)
        self.combo_diametro = QComboBox(self)
        self.combo_rotacao = QComboBox(self)
        
        # Adiciona o item neutro "Selecione" a cada QComboBox
        self.combo_marca.addItem("Selecione")
        self.combo_modelo.addItem("Selecione")
        self.combo_diametro.addItem("Selecione")
        self.combo_rotacao.addItem("Selecione")
        
        self.layout.addRow("Marca:", self.combo_marca)
        self.layout.addRow("Modelo:", self.combo_modelo)
        
        # Adiciona o botão "Mostrar Gráfico da Bomba" abaixo do segundo combo (Modelo)
        self.btn_mostrar_grafico = QPushButton("Mostrar Gráfico da Bomba", self)
        self.layout.addRow("", self.btn_mostrar_grafico)
        
        self.layout.addRow("Diametro:", self.combo_diametro)
        self.layout.addRow("Rotação:", self.combo_rotacao)
        
        # Inicialmente, apenas o QComboBox de Marca está habilitado
        self.combo_modelo.setEnabled(False)
        self.combo_diametro.setEnabled(False)
        self.combo_rotacao.setEnabled(False)
        
        self.load_marcas()
        
        # Conecta os sinais para atualização encadeada
        self.combo_marca.currentIndexChanged.connect(self.on_marca_changed)
        self.combo_modelo.currentIndexChanged.connect(self.on_modelo_changed)
        self.combo_diametro.currentIndexChanged.connect(self.on_diametro_changed)
        
        # Configura o timer para monitorar alterações no banco de dados
        self.last_db_mod_time = os.path.getmtime(DB_PATH)
        self.timer = QTimer(self)
        self.timer.setInterval(2000)  # Verifica a cada 2 segundos
        self.timer.timeout.connect(self.check_db_update)
        self.timer.start()
        
        # Conecta o botão "Mostrar Gráfico da Bomba" (funcionalidade placeholder)
        self.btn_mostrar_grafico.clicked.connect(self.mostrar_grafico_bomba)
    
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
        
        # Reinicia os QComboBox inferiores
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
        # Implementação placeholder: aqui você pode abrir uma nova janela com o gráfico da bomba selecionada.
        print("Mostrar gráfico da bomba (placeholder).")


class PumpListSelectionWidget(QGroupBox):
    """Widget com lista de bombas e botões para selecionar bomba e mostrar gráfico."""
    def __init__(self, parent=None):
        super().__init__("Seleção de Bomba (Lista)", parent)
        self.system_curve = None
        self.target_flow = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Botão "Selecionar Bomba" acima da lista
        self.btn_selecionar = QPushButton("Selecionar Bomba", self)
        layout.addWidget(self.btn_selecionar)
        self.btn_selecionar.clicked.connect(self.selecionar_bomba)
        
        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)
    
    def set_system_curve(self, system_curve, target_flow):
        """
        Define os parâmetros necessários para a seleção automática de bomba:
         - system_curve: coeficientes da curva do sistema (polinômio de grau 5)
         - target_flow: fluxo alvo (valor máximo), normalmente obtido de pump_selection_tab.py
        """
        self.system_curve = system_curve
        self.target_flow = target_flow
    
    def selecionar_bomba(self):
        if self.system_curve is None or self.target_flow is None:
            print("Parâmetros do sistema não definidos.")
            return
        # Chama a função auto_pump_selection passando:
        # - coeficientes da curva do sistema,
        # - fluxo mínimo = 0,
        # - fluxo máximo = target_flow
        pumps = auto_pump_selection(self.system_curve, 0, self.target_flow)
        # Atualiza a lista com os resultados
        self.list_widget.clear()
        if isinstance(pumps, str):
            self.list_widget.addItem(pumps)
        elif pumps:
            for pump in pumps:
                item_text = (f"Marca: {pump['marca']}, Modelo: {pump['modelo']}, "
                             f"Diametro: {pump['diametro']}, Rotação: {pump['rotacao']}")
                self.list_widget.addItem(item_text)
        else:
            self.list_widget.addItem("Nenhuma bomba encontrada.")

