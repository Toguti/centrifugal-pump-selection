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
from typing import Dict, Any
import logging

# Importa a função de seleção automática de bomba
from UI.func.auto_pump_selection import auto_pump_selection

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
    Obtém os dados do SystemInputWidget para a seleção de bombas.
    """
    def __init__(self, system_input_widget, fluid_prop_input_widget, parent=None):
        super().__init__(parent)
        self.system_input_widget = system_input_widget
        self.fluid_prop_input_widget = fluid_prop_input_widget
        self.system_curve = None
        self.target_flow = None
        self.pumps = []
        self.selected_pump_index = None
        
        # Conectar ao sinal de cálculo concluído do SystemInputWidget
        self.system_input_widget.calculoCompleto.connect(self.atualizar_dados_sistema)
        
        self.init_ui()
        self.setup_db_timer()
    
    def init_ui(self):
        self.setWindowTitle("Seleção de Bombas")
        self.resize(800, 600)
        main_layout = QHBoxLayout(self)
        
        # Área Esquerda: resultados e botões
        left_widget = QWidget(self)
        left_layout = QVBoxLayout(left_widget)
        
        # -- Informações do Sistema --
        system_info_group = QGroupBox("Informações do Sistema", left_widget)
        system_info_layout = QFormLayout(system_info_group)
        
        # Campo de vazão de projeto - renomeado para maior clareza
        self.system_target_flow = QLineEdit()
        self.system_target_flow.setReadOnly(True)
        system_info_layout.addRow("Vazão Total do Sistema:", self.system_target_flow)
        
        # Novo campo para Head de projeto
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
        self.combo_n_bombas.addItems([str(i) for i in range(1, 10)])  # 1 a 9
        self.combo_n_bombas.currentIndexChanged.connect(self.atualizar_grafico_bombas_paralelo)
        system_info_layout.addRow(label_n_bombas, self.combo_n_bombas)
        
        # Campo para vazão por bomba
        self.vazao_por_bomba = QLineEdit()
        self.vazao_por_bomba.setReadOnly(True)
        system_info_layout.addRow("Vazão por Bomba de Projeto:", self.vazao_por_bomba)
        
        left_layout.addWidget(system_info_group)
        
        # -- QGroupBox: Seleção de Bomba (Lista) --
        self.pump_list_box = QGroupBox("Seleção de Bomba", left_widget)
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

        # Campo para Diâmetro do rotor
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
        
        # Campo para margem de NPSH
        self.result_npsh_comparison = QLineEdit()
        self.result_npsh_comparison.setReadOnly(True)
        data_layout.addRow("Margem de NPSH:", self.result_npsh_comparison)

        left_layout.addWidget(self.pump_data_box)
        left_layout.addStretch()
        
        # Botões finais
        button_layout = QHBoxLayout()
        
        self.btn_adicionar_curva = QPushButton("Adicionar Nova Curva", left_widget)
        self.btn_adicionar_curva.clicked.connect(self.abrir_curve_input_dialog)
        button_layout.addWidget(self.btn_adicionar_curva)
        
        left_layout.addLayout(button_layout)
        
        # Área Direita: Gráfico
        right_widget = QWidget(self)
        right_layout = QVBoxLayout(right_widget)
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("Vazão (m³/h)")
        self.ax.set_ylabel("Head (m)")
        self.ax.set_title("Curva do Sistema x Curva da Bomba")
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
    
    def atualizar_dados_sistema(self):
        """
        Atualiza os dados do sistema após o cálculo no SystemInputWidget.
        """
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
        
        # Calcular vazão por bomba (depende do número de bombas)
        n_bombas = int(self.combo_n_bombas.currentText())
        if self.target_flow is not None:
            vazao_por_bomba = self.target_flow / n_bombas
            self.vazao_por_bomba.setText(f"{vazao_por_bomba:.2f} m³/h")
        
        # Habilitar o botão de seleção de bomba
        self.btn_selecionar_bomba.setEnabled(True)
        
        # Atualizar o gráfico para o número atual de bombas em paralelo
        self.atualizar_grafico_bombas_paralelo()
    
    # Adicionar função para atualizar bombas quando o número de bombas é alterado
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
        self.system_target_flow.setText(f"{self.target_flow:.2f} m³/h (total para {n_bombas} bomba{'s' if n_bombas > 1 else ''})")
        self.vazao_por_bomba.setText(f"{vazao_por_bomba:.2f} m³/h por bomba")
        
        # Ajustar a curva do sistema para o número atual de bombas
        self.system_curve_adjusted = self.adjust_system_curve_for_parallel_pumps(self.system_curve, n_bombas)
        
        # NOVA FUNCIONALIDADE: Limpar a seleção atual
        
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
        
        # Criar flow_values para o gráfico
        flow_values = np.linspace(0, self.target_flow * 1.4, 500)
        
        # Mostrar apenas a curva do sistema (sem bomba selecionada)
        self.atualizar_plot(flow_values, self.system_curve)
        
    
    def formatar_item_lista(self, pump: Dict[str, Any]) -> tuple:
        """
        Formata o texto do item e o tooltip a partir dos dados da bomba.
        Trata cuidadosamente a estrutura de 'intersecoes' para evitar erros.
        Considera o número de bombas em paralelo.
        """
        # Obter o número de bombas em paralelo
        n_bombas = int(self.combo_n_bombas.currentText())
        
        # Valor de vazão de operação, com validação e tratamento de erros
        try:
            # Verificar a estrutura de intersecoes e obter o valor de vazão (por bomba)
            intersecoes = pump.get('intersecoes', [[0.0, 0.0]])
            if isinstance(intersecoes, list) and len(intersecoes) > 0:
                if isinstance(intersecoes[0], list) and len(intersecoes[0]) > 0:
                    vazao_bomba = intersecoes[0][0]  # Estrutura: [[x, y], ...]
                else:
                    vazao_bomba = intersecoes[0]  # Estrutura: [x, y, ...]
            else:
                vazao_bomba = 0.0
                
            # Verificar se temos a vazão total do sistema pré-calculada
            if 'system_flow_total' in pump:
                vazao_total = pump['system_flow_total']
            else:
                vazao_total = vazao_bomba * n_bombas
                
        except (IndexError, TypeError):
            vazao_bomba = 0.0
            vazao_total = 0.0
            print(f"Erro ao acessar estrutura de interseções: {pump.get('intersecoes')}")

        item_text = (f"Marca: {pump.get('marca', 'N/D')}, Modelo: {pump.get('modelo', 'N/D')}, "
                    f"Diâmetro: {pump.get('diametro', 'N/D')}, Rotação: {pump.get('rotacao', 'N/D')}, "
                    f"Eff.: {pump.get('pump_eff', 0):.2f}%")
        
        npsh_disponivel = self.system_input_widget.get_npsh_disponivel()
        margem_npsh = npsh_disponivel - pump.get('pump_npshr', 0) if npsh_disponivel is not None else 0
        
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
        # Verificar se os dados do sistema estão disponíveis
        if self.system_curve is None or self.target_flow is None:
            QMessageBox.warning(
                self, 
                "Aviso", 
                "É necessário calcular o sistema primeiro. Vá para a aba 'Sistema' e clique em 'Calcular Curva do Sistema'."
            )
            return
        
        # Obter o NPSH disponível
        npsh_disponivel = self.system_input_widget.get_npsh_disponivel()
        if npsh_disponivel is None or npsh_disponivel <= 0:
            QMessageBox.critical(self, "Erro", "NPSH disponível não calculado ou inválido.")
            return
        
        # Obter o número de bombas em paralelo
        n_bombas = int(self.combo_n_bombas.currentText())
        
        # Ajustar a vazão alvo para o número de bombas em paralelo
        # Cada bomba precisará fornecer apenas uma fração da vazão total
        vazao_por_bomba = self.target_flow / n_bombas
        
        logging.info(f"NPSH disponível utilizado: {npsh_disponivel:.2f} m")
        logging.info(f"Número de bombas em paralelo: {n_bombas}")
        logging.info(f"Vazão total do sistema: {self.target_flow:.2f} m³/h")
        logging.info(f"Vazão alvo por bomba: {vazao_por_bomba:.2f} m³/h")
        
        # Criar uma curva de sistema ajustada para o número de bombas em paralelo
        # Usamos uma abordagem baseada em amostras de pontos
        
        system_curve_adjusted = self.adjust_system_curve_for_parallel_pumps(self.system_curve, n_bombas)
        self.system_curve_adjusted = system_curve_adjusted  # Armazenar para uso posterior
        # Selecionar bombas usando a curva ajustada e a vazão por bomba
        pumps = auto_pump_selection(system_curve_adjusted, vazao_por_bomba)
        logging.info(f"Bombas selecionadas antes do filtro NPSH: {len(pumps) if isinstance(pumps, list) else 0}")
        
        self.list_widget.clear()
        self.selected_pump_index = None
        

        if isinstance(pumps, str):
            self.list_widget.addItem(pumps)
            self.pumps = []
            return
        
        # Filtrar bombas com base no critério NPSH
        pumps_filtered = []
        filtered_out_count = 0
        
        for pump in pumps:
            # Verificar se o NPSH requerido da bomba é menor que o NPSH disponível
            if pump['pump_npshr'] < npsh_disponivel:
                # Calcular a vazão total do sistema para esta bomba
                try:
                    # Obter a vazão do ponto de interseção (vazão por bomba) e o head correspondente
                    intersecoes = pump.get('intersecoes', [[0.0, 0.0]])
                    if isinstance(intersecoes, list) and len(intersecoes) > 0:
                        if isinstance(intersecoes[0], list) and len(intersecoes[0]) > 0:
                            vazao_bomba = intersecoes[0][0]
                            head_value = intersecoes[0][1] if len(intersecoes[0]) > 1 else np.polyval(system_curve_adjusted, vazao_bomba)
                        else:
                            vazao_bomba = intersecoes[0]
                            head_value = intersecoes[1] if len(intersecoes) > 1 else np.polyval(system_curve_adjusted, vazao_bomba)
                    else:
                        vazao_bomba = 0.0
                        head_value = 0.0
                    
                    # Calcular a vazão total do sistema (vazão por bomba * número de bombas)
                    vazao_total = vazao_bomba * n_bombas
                    
                    # Armazenar os valores calculados para uso posterior
                    pump['vazao_bomba'] = vazao_bomba
                    pump['vazao_total'] = vazao_total
                    pump['head_value'] = head_value
                    
                    # Criar um ponto de interseção próprio para este número de bombas
                    pump['ponto_intersecao'] = [vazao_bomba, head_value]
                    
                except Exception as e:
                    print(f"Erro ao processar interseções: {e}")
                    # Em caso de erro, adiciona valores padrão
                    pump['vazao_bomba'] = vazao_por_bomba
                    pump['vazao_total'] = vazao_por_bomba * n_bombas
                    pump['head_value'] = np.polyval(system_curve_adjusted, vazao_por_bomba)
                    pump['ponto_intersecao'] = [vazao_por_bomba, pump['head_value']]
                    
                pumps_filtered.append(pump)
            else:
                filtered_out_count += 1
                logging.info(f"Bomba filtrada por NPSH: {pump['marca']} {pump['modelo']} - "
                            f"NPSHr: {pump['pump_npshr']:.2f} m > NPSHd: {npsh_disponivel:.2f} m")
        
        logging.info(f"Bombas removidas pelo filtro NPSH: {filtered_out_count}")
        
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
        
        # Adicionar as bombas filtradas e ordenadas à lista
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
        
        Gera um conjunto de pontos a partir da curva original,
        divide os valores de vazão (eixo x) pelo número de bombas,
        e realiza um novo ajuste polinomial de grau 5.
        
        Parâmetros:
            original_curve: coeficientes da curva do sistema original
            n_bombas: número de bombas em paralelo
            
        Retorna:
            Novos coeficientes para a curva ajustada
        """

        
        # Determinar um intervalo apropriado para os valores de vazão
        # Usar o valor máximo de vazão do sistema e adicionar uma margem
        if hasattr(self, 'target_flow') and self.target_flow is not None:
            max_flow = self.target_flow * 1.4  # Usar o mesmo fator que é usado em outras partes do código
        else:
            max_flow = 100.0  # Valor padrão se não houver informação disponível
        
        # Gerar conjunto de 100 valores de vazão (eixo x)
        x_original = np.linspace(0.001, max_flow, 100)  # Evitando o zero para prevenir divisão por zero
        
        # Calcular os valores de head correspondentes usando a curva original
        y_original = np.polyval(original_curve, x_original)
        
        # Ajustar os valores de vazão dividindo pelo número de bombas
        x_adjusted = x_original / n_bombas
        
        # Realizar um novo ajuste polinomial de grau 5 para os pontos ajustados
        adjusted_curve = np.polyfit(x_adjusted, y_original, 5)
        
        return adjusted_curve
    
    def abrir_curve_input_dialog(self):
        dialog = CurveInputDialog(self)
        dialog.exec()
    
    def atualizar_plot(self, flow_values, system_head_values_coef, pump_head_coef_values=None, pump_vazao_min=None, pump_vazao_max=None, intersection_point=None):
        """
        Atualiza o gráfico com as curvas do sistema e da bomba.
        Usa o ponto de interseção atualizado.
        """
        try:
            self.ax.clear()
            
            # Obter o número de bombas em paralelo
            n_bombas = int(self.combo_n_bombas.currentText())
            
            # Plotar a curva do sistema 
            if system_head_values_coef is not None:
                # Gerar vazões para o eixo X, com passo adequado
                system_flow_values = np.linspace(0.001, max(flow_values) * 1.1, 500)
                
                # Calcular heads para a curva do sistema original (vazão total)
                system_head_values = np.polyval(system_head_values_coef, system_flow_values)
                
                # Dividir vazões pelo número de bombas para plotagem
                system_flow_values_ajustado = system_flow_values / n_bombas
                
                # Plotar curva do sistema
                self.ax.plot(system_flow_values_ajustado, system_head_values, 
                            linestyle='-', color='blue', linewidth=2, 
                            label='Curva do Sistema')
            
            # Plotar curva da bomba
            if pump_head_coef_values is not None and pump_vazao_min is not None and pump_vazao_max is not None:
                # Gerar valores para curva da bomba
                pump_flow_values = np.linspace(pump_vazao_min, pump_vazao_max, 500)
                pump_head_values = np.polyval(pump_head_coef_values, pump_flow_values)
                
                # Plotar curva da bomba
                self.ax.plot(pump_flow_values, pump_head_values, 
                            linestyle='--', color='green', linewidth=2, 
                            label='Curva da Bomba')
                
                # Plotar ponto de interseção
                if intersection_point is not None:
                    try:
                        # Se estamos na função on_item_double_clicked, intersection_point 
                        # será o valor armazenado em pump['ponto_intersecao']
                        # que já foi calculado corretamente para o número atual de bombas
                        if isinstance(intersection_point, list) and len(intersection_point) >= 2:
                            x, y = intersection_point[0], intersection_point[1]
                            
                            # Marcar o ponto de interseção no gráfico
                            self.ax.plot(x, y, 'ro', markersize=8, label='Ponto de Operação')
                            
                            # Adicionar linhas tracejadas até os eixos
                            self.ax.axhline(y=y, color='r', linestyle=':', alpha=0.5)
                            self.ax.axvline(x=x, color='r', linestyle=':', alpha=0.5)
                            
                            # Opcional: Adicionar texto com o valor do ponto
                            self.ax.annotate(f'({x:.1f}, {y:.1f})', 
                                            xy=(x, y), 
                                            xytext=(10, 10),
                                            textcoords='offset points',
                                            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
                        
                    except Exception as e:
                        print(f"Erro ao plotar ponto de interseção: {e}")
            
            # Configurações do gráfico
            self.ax.set_xlabel("Vazão por Bomba (m³/h)")
            self.ax.set_ylabel("Head (m)")
            self.ax.set_title(f"Curva do Sistema x Curva da Bomba ({n_bombas} bomba{'s' if n_bombas > 1 else ''} em paralelo)")
            self.ax.legend(loc='best')
            self.ax.set_ylim(bottom=0)  # Limite inferior do eixo y para 0
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.canvas.draw()
            
        except Exception as e:
            print(f"Erro ao atualizar o gráfico: {e}")

            
    def on_item_double_clicked(self, item):
        """
        Ao dar duplo clique em um item da lista, atualiza os campos do grupo Dados da Bomba.
        Usa os dados de interseção já calculados para o número atual de bombas.
        """
        index = self.list_widget.row(item)
        self.selected_pump_index = index  # Armazenar o índice da bomba selecionada
        
        try:
            pump = self.pumps[index]
        except IndexError:
            print("Índice inválido no array de bombas.")
            return

        # Obter o número de bombas em paralelo
        n_bombas = int(self.combo_n_bombas.currentText())

        # Usar os valores já calculados e armazenados na bomba
        vazao_bomba = pump.get('vazao_bomba', 0.0)
        vazao_total = pump.get('vazao_total', 0.0)
        head_value = pump.get('head_value', 0.0)
        
        # Se os valores não estiverem pré-calculados (improvável com as alterações),
        # calcular a partir do início
        if vazao_bomba == 0.0 or vazao_total == 0.0 or head_value == 0.0:
            try:
                # Recalcular usando intersecoes originais
                intersecoes = pump.get('intersecoes', [[0.0, 0.0]])
                if isinstance(intersecoes, list) and len(intersecoes) > 0:
                    if isinstance(intersecoes[0], list) and len(intersecoes[0]) > 0:
                        vazao_bomba = intersecoes[0][0]
                        head_value = intersecoes[0][1] if len(intersecoes[0]) > 1 else np.polyval(self.system_curve_adjusted, vazao_bomba)
                    else:
                        vazao_bomba = intersecoes[0]
                        head_value = intersecoes[1] if len(intersecoes) > 1 else np.polyval(self.system_curve_adjusted, vazao_bomba)
                
                vazao_total = vazao_bomba * n_bombas
                
                # Armazenar os valores calculados
                pump['vazao_bomba'] = vazao_bomba
                pump['vazao_total'] = vazao_total
                pump['head_value'] = head_value
                pump['ponto_intersecao'] = [vazao_bomba, head_value]
                
            except Exception as e:
                print(f"Erro ao recalcular ponto de operação: {e}")
                vazao_bomba = self.target_flow / n_bombas
                vazao_total = self.target_flow
                head_value = np.polyval(self.system_curve, vazao_total)

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
        
        # Atualiza o campo com o diâmetro do rotor
        self.result_rotor_diametro.setText(f"{pump.get('diametro', 'N/D')} mm")

        # Calcular e exibir a margem de NPSH
        npsh_disponivel = self.system_input_widget.get_npsh_disponivel()
        npsh_requerido = pump.get('pump_npshr', 0)
        if npsh_disponivel is not None:
            margem_npsh = npsh_disponivel - npsh_requerido
            margem_str = f"{margem_npsh:.2f}".replace('.', ',')

            # Colorir o campo de acordo com a margem
            if margem_npsh < 0.5:
                self.result_npsh_comparison.setStyleSheet("background-color: #ffcccc;")  # Vermelho claro
            elif margem_npsh < 1.0:
                self.result_npsh_comparison.setStyleSheet("background-color: #ffffcc;")  # Amarelo claro
            else:
                self.result_npsh_comparison.setStyleSheet("background-color: #ccffcc;")  # Verde claro

            self.result_npsh_comparison.setText(margem_str + " m")
        else:
            self.result_npsh_comparison.setText("N/D")

        # Atualizar o gráfico com a curva do sistema, curva da bomba e ponto de interseção
        try:
            pump_head_coef_values = pump.get('pump_coef_head')
            pump_vazao_min = pump.get('pump_vazao_min', 0)
            pump_vazao_max = pump.get('pump_vazao_max', 100)
            
            # Usar o ponto de interseção corretamente calculado
            intersection_point = pump.get('ponto_intersecao', [vazao_bomba, head_value])
            
            # Atualiza o gráfico com a curva do sistema e a curva da bomba
            flow_values = np.linspace(0, max(pump_vazao_max, self.target_flow * 1.4), 500)
            self.atualizar_plot(flow_values, self.system_curve, pump_head_coef_values, 
                            pump_vazao_min, pump_vazao_max, intersection_point)
        except Exception as e:
            print(f"Erro ao atualizar o gráfico: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Widgets dummy para injeção; substitua pelos reais conforme necessário
    system_input_widget = QWidget()
    fluid_prop_input_widget = QWidget()
    main_widget = PumpSelectionWidget(system_input_widget, fluid_prop_input_widget)
    main_widget.show()
    sys.exit(app.exec())
