import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import logging
from typing import Dict, List, Optional, Tuple, Any, Union

class PumpGraphComponent(QWidget):
    """
    Componente para exibição de múltiplos gráficos relacionados ao desempenho de bombas.
    
    Exibe quatro gráficos:
    1. Vazão x Head (40% da altura vertical)
    2. Vazão x NPSHr (20% da altura vertical)
    3. Vazão x Potência (20% da altura vertical)
    4. Vazão x Eficiência (20% da altura vertical)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.system_max_head = None  # Para armazenar o head máximo encontrado na curva do sistema
        self.system_max_flow = None  # Para armazenar a vazão máxima encontrada na curva do sistema
        self.system_flow_range = None  # Para armazenar o range do eixo X que será comum para todos os gráficos
        self.head_scale_set = False  # Flag para indicar se a escala do gráfico Head já foi definida
        
        # Armazenar referências às linhas do sistema para preservá-las
        self.system_head_line = None  # Linha do gráfico Head x Vazão
        self.system_npsh_line = None  # Linha do gráfico NPSH disponível
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do usuário com os múltiplos gráficos."""
        # Layout principal sem margens
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remover margens do layout
        layout.setSpacing(0)  # Remover espaçamento entre widgets
        
        # Criar figura com subplots proporcional e margens reduzidas
        self.figure = Figure(figsize=(8, 12))
        self.figure.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.05)  # Reduzir margens da figura
        
        # Criar subplots com diferentes tamanhos (Head: 2/5, outros: 1/5 cada)
        # Total de 5 unidades de altura, com espaçamento vertical reduzido
        gs = self.figure.add_gridspec(5, 1, hspace=0.25)  # Espaçamento vertical reduzido
        
        # Criar os eixos para cada gráfico com as proporções especificadas
        self.ax_head = self.figure.add_subplot(gs[0:2, 0])   # 2/5 para Head (40%)
        self.ax_npshr = self.figure.add_subplot(gs[2, 0])    # 1/5 para NPSHr (20%)
        self.ax_power = self.figure.add_subplot(gs[3, 0])    # 1/5 para Potência (20%)
        self.ax_eff = self.figure.add_subplot(gs[4, 0])      # 1/5 para Eficiência (20%)
        
        # Configurações iniciais dos gráficos
        self.setup_plots()
        
        # Criar o canvas
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
    
    def setup_plots(self):
        """Configuração inicial dos gráficos."""
        # Gráfico de Head
        self.ax_head.set_ylabel("Head (m)")
        self.ax_head.set_title("Curva do Sistema x Curva da Bomba")
        self.ax_head.grid(True, linestyle='--', alpha=0.7)
        self.ax_head.set_ylim(bottom=0)  # Começar em zero para melhor visualização
        self.ax_head.tick_params(labelbottom=False)  # Remover labels do eixo X
        
        # Gráfico de NPSHr
        self.ax_npshr.set_ylabel("NPSH (m)")
        self.ax_npshr.set_title("NPSHr x NPSH disponível")
        self.ax_npshr.grid(True, linestyle='--', alpha=0.7)
        self.ax_npshr.set_ylim(bottom=0)  # Começar em zero para melhor visualização
        self.ax_npshr.tick_params(labelbottom=False)  # Remover labels do eixo X
        
        # Gráfico de Potência
        self.ax_power.set_ylabel("Potência (cv)")
        self.ax_power.set_title("Curva de Potência")
        self.ax_power.grid(True, linestyle='--', alpha=0.7)
        self.ax_power.set_ylim(bottom=0)  # Começar em zero para melhor visualização
        self.ax_power.tick_params(labelbottom=False)  # Remover labels do eixo X
        
        # Gráfico de Eficiência - Único com label do eixo X
        self.ax_eff.set_xlabel("Vazão (m³/h)")
        self.ax_eff.set_ylabel("Eficiência (%)")
        self.ax_eff.set_title("Curva de Eficiência")
        self.ax_eff.grid(True, linestyle='--', alpha=0.7)
        self.ax_eff.set_ylim(bottom=0)  # Começar em zero para melhor visualização
    
    def update_parallel_pumps(self, system_curve, flow_values, n_bombas, npsh_disponivel):
        """
        Atualiza os gráficos quando o número de bombas em paralelo é alterado.
        Recalcula as escalas e a curva do sistema para o novo número de bombas.
        
        Parâmetros:
            system_curve: Coeficientes da curva do sistema original
            flow_values: Valores de vazão para plotagem
            n_bombas: Novo número de bombas em paralelo
            npsh_disponivel: NPSH disponível do sistema
        """
        try:
            logging.info(f"Atualizando gráficos para {n_bombas} bombas em paralelo")
            
            # Limpar apenas os elementos da bomba, preservando as escalas
            self.clear_pump_plots()
            
            # Verificar se temos dados suficientes
            if system_curve is None:
                logging.warning("System curve não fornecida para atualização de bombas paralelas")
                self.canvas.draw()
                return
                
            # Se não houver flow_values, criar um intervalo padrão
            if flow_values is None or len(flow_values) == 0:
                flow_values = np.linspace(0.001, 100, 500)
            
            # Limpar todas as linhas existentes (incluindo as do sistema)
            self.ax_head.clear()
            self.ax_npshr.clear()
            self.ax_power.clear()
            self.ax_eff.clear()
            
            # Refazer a configuração básica
            self.setup_plots()
            
            # Plotar a nova curva do sistema com o número atualizado de bombas
            self.plot_system_curve(system_curve, flow_values, n_bombas, True)
            
            # Plotar NPSH disponível
            if npsh_disponivel is not None and npsh_disponivel > 0:
                self.plot_npsh_disponivel(flow_values, npsh_disponivel)
            
            # Recalcular e aplicar novas escalas baseadas no novo número de bombas
            if self.system_max_flow is not None and self.system_max_head is not None:
                # Arredondamento para cima para obter limites "bonitos"
                max_flow = self.system_max_flow
                max_flow_with_margin = np.ceil((max_flow * 1.1) / 5) * 5
                
                # Dividir vazão máxima pelo número de bombas para plotagem
                system_flow_range = [0, max_flow_with_margin / n_bombas]
                self.system_flow_range = system_flow_range
                
                # Ajustar escala do eixo X para todos os gráficos
                self.ax_head.set_xlim(*system_flow_range)
                self.ax_npshr.set_xlim(*system_flow_range)
                self.ax_power.set_xlim(*system_flow_range)
                self.ax_eff.set_xlim(*system_flow_range)
                
                # Manter a mesma escala Y para o Head
                max_head = self.system_max_head
                max_head_with_margin = np.ceil((max_head * 1.1) / 5) * 5
                self.ax_head.set_ylim(0, max_head_with_margin)
                
                logging.info(f"Escalas atualizadas para bombas em paralelo: X=[0, {system_flow_range[1]:.2f}]")
            
            # Finalizar
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            logging.error(f"Erro ao atualizar para bombas em paralelo: {e}", exc_info=True)

    def setup_plots_without_scale_reset(self):
        """Configuração de gráficos sem alterar escalas."""
        # Gráfico de Head
        self.ax_head.set_ylabel("Head (m)")
        self.ax_head.set_title("Curva do Sistema x Curva da Bomba")
        self.ax_head.grid(True, linestyle='--', alpha=0.7)
        self.ax_head.tick_params(labelbottom=False)  # Remover labels do eixo X
        
        # Gráfico de NPSHr
        self.ax_npshr.set_ylabel("NPSH (m)")
        self.ax_npshr.set_title("NPSHr x NPSH disponível")
        self.ax_npshr.grid(True, linestyle='--', alpha=0.7)
        self.ax_npshr.tick_params(labelbottom=False)  # Remover labels do eixo X
        
        # Gráfico de Potência
        self.ax_power.set_ylabel("Potência (cv)")
        self.ax_power.set_title("Curva de Potência")
        self.ax_power.grid(True, linestyle='--', alpha=0.7)
        self.ax_power.tick_params(labelbottom=False)  # Remover labels do eixo X
        
        # Gráfico de Eficiência - Único com label do eixo X
        self.ax_eff.set_xlabel("Vazão (m³/h)")
        self.ax_eff.set_ylabel("Eficiência (%)")
        self.ax_eff.set_title("Curva de Eficiência")
        self.ax_eff.grid(True, linestyle='--', alpha=0.7)



    def clear_plots(self):
        """Limpa completamente todos os gráficos - usar apenas para novo sistema."""
        self.ax_head.clear()
        self.ax_npshr.clear()
        self.ax_power.clear()
        self.ax_eff.clear()
        self.setup_plots()
        
        # Resetar as referências às linhas do sistema
        self.system_head_line = None
        self.system_npsh_line = None
    
    def clear_pump_plots(self):
        """
        Limpa apenas os elementos da bomba nos gráficos, 
        mantendo as escalas (mas não necessariamente as curvas do sistema).
        """
        # Capturar as escalas atuais antes de limpar
        head_x_lim = self.ax_head.get_xlim()
        head_y_lim = self.ax_head.get_ylim()
        npshr_x_lim = self.ax_npshr.get_xlim()
        npshr_y_lim = self.ax_npshr.get_ylim()
        power_x_lim = self.ax_power.get_xlim()
        power_y_lim = self.ax_power.get_ylim()
        eff_x_lim = self.ax_eff.get_xlim()
        eff_y_lim = self.ax_eff.get_ylim()
        
        # Remover apenas as linhas relacionadas à bomba, mantendo as do sistema
        # Identificar linhas a serem mantidas e removidas
        head_lines_to_keep = []
        head_lines_to_remove = []
        
        for line in self.ax_head.lines:
            if line.get_label() == 'Curva do Sistema':
                head_lines_to_keep.append(line)
            else:
                head_lines_to_remove.append(line)
        
        # Remover as linhas da bomba
        for line in head_lines_to_remove:
            line.remove()
        
        # Fazer o mesmo para os demais gráficos
        npshr_lines_to_keep = []
        npshr_lines_to_remove = []
        
        for line in self.ax_npshr.lines:
            if line.get_label() == 'NPSH disponível':
                npshr_lines_to_keep.append(line)
            else:
                npshr_lines_to_remove.append(line)
        
        for line in npshr_lines_to_remove:
            line.remove()
        
        # Limpar completamente os gráficos de potência e eficiência (não têm curvas do sistema)
        self.ax_power.clear()
        self.ax_eff.clear()
        
        # Remover outros elementos como textos, anotações, etc.
        for txt in self.ax_head.texts:
            txt.remove()
        
        for txt in self.ax_npshr.texts:
            txt.remove()
        
        # Refazer configurações básicas sem alterar escalas
        self.setup_plots_without_scale_reset()
        
        # Restaurar escalas
        self.ax_head.set_xlim(head_x_lim)
        self.ax_head.set_ylim(head_y_lim)
        self.ax_npshr.set_xlim(npshr_x_lim)
        self.ax_npshr.set_ylim(npshr_y_lim)
        self.ax_power.set_xlim(power_x_lim)
        self.ax_power.set_ylim(power_y_lim)
        self.ax_eff.set_xlim(eff_x_lim)
        self.ax_eff.set_ylim(eff_y_lim)
        
        # Atualizar legendas para os gráficos que mantiveram linhas
        if len(self.ax_head.lines) > 0:
            self.ax_head.legend(loc='best')
        if len(self.ax_npshr.lines) > 0:
            self.ax_npshr.legend(loc='best')
            
        logging.info("Limpos apenas os elementos da bomba, preservando escalas")


    
    def reset_scales(self):
        """Reseta as escalas e flags quando um novo cálculo do sistema é feito."""
        self.head_scale_set = False
        self.system_flow_range = None
    
    def update_plots(self, system_curve: Optional[np.ndarray], 
                 pump_data: Optional[Dict[str, Any]] = None,
                 flow_values: Optional[np.ndarray] = None,
                 n_bombas: int = 1,
                 intersection_point: Optional[List] = None,
                 npsh_disponivel: Optional[float] = None,
                 is_new_system: bool = False):
        """
        Atualiza todos os gráficos com os dados fornecidos.

        Parâmetros:
            system_curve (numpy.ndarray): Coeficientes da curva do sistema
            pump_data (dict): Dados da bomba selecionada (com coeficientes das curvas)
            flow_values (numpy.ndarray): Valores de vazão para plotagem
            n_bombas (int): Número de bombas em paralelo
            intersection_point (list): Ponto de interseção [vazão, head]
            npsh_disponivel (float): NPSH disponível do sistema
            is_new_system (bool): Indica se é um novo cálculo do sistema (reseta scales)
        """
        try:
            # Registrar os dados recebidos para depuração
            logging.info(f"Atualizando gráficos: system_curve={type(system_curve) if system_curve is not None else None}")
            logging.info(f"Bomba selecionada: {pump_data.get('marca', 'N/D')} {pump_data.get('modelo', 'N/D')}") if pump_data else logging.info("Nenhuma bomba selecionada")
            logging.info(f"Número de bombas: {n_bombas}")
            logging.info(f"NPSH disponível: {npsh_disponivel}")
            logging.info(f"Ponto de interseção: {intersection_point}")
            logging.info(f"É novo sistema: {is_new_system}")
            
            # Reiniciar escalas se for um novo cálculo do sistema
            if is_new_system:
                logging.info("Novo sistema: Resetando escalas e limpando todos os gráficos")
                self.reset_scales()
                # Limpar completamente todos os gráficos para novo sistema
                self.clear_plots()
            else:
                # Para seleção de bomba, limpar apenas os elementos da bomba
                logging.info("Seleção de bomba: Preservando escalas e limpando apenas elementos da bomba")
                self.clear_pump_plots()
            
            # Verificar se temos dados suficientes para plotar
            if system_curve is None:
                logging.warning("System curve não fornecida para plotagem")
                self.canvas.draw()
                return
                
            # Se não houver flow_values, criar um intervalo padrão
            if flow_values is None or len(flow_values) == 0:
                logging.info("Usando valores de vazão padrão")
                flow_values = np.linspace(0.001, 100, 500)
            
            # Plotar curva do sistema no gráfico principal (Head) apenas se for um novo sistema
            # ou se a curva do sistema ainda não existe
            if is_new_system or not any(line.get_label() == 'Curva do Sistema' for line in self.ax_head.lines):
                logging.info("Plotando nova curva do sistema")
                self.plot_system_curve(system_curve, flow_values, n_bombas, is_new_system)
            
            # Plotar NPSH disponível (mesmo que não haja bomba selecionada)
            # apenas se for um novo sistema ou se não já existe
            if npsh_disponivel is not None and npsh_disponivel > 0:
                if is_new_system or not any(line.get_label() == 'NPSH disponível' for line in self.ax_npshr.lines):
                    logging.info("Plotando novo NPSH disponível")
                    self.plot_npsh_disponivel(flow_values, npsh_disponivel)
            
            # Se tivermos dados de bomba, plotar as curvas da bomba
            if pump_data is not None:
                logging.info("Plotando curvas da bomba")
                self.plot_pump_curves(pump_data, flow_values, intersection_point, npsh_disponivel)
            
            # Ajuste automático da escala dos gráficos
            self.adjust_plot_scales(system_curve, pump_data, flow_values, n_bombas, npsh_disponivel, is_new_system)
            
            # Aplicar formatação e configurações finais
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            logging.error(f"Erro ao atualizar gráficos: {e}", exc_info=True)

    
    def adjust_plot_scales(self, system_curve, pump_data, flow_values, n_bombas, npsh_disponivel, is_new_system):
        """
        Ajusta automaticamente a escala dos gráficos para melhor visualização.
        
        Parâmetros:
            system_curve: Coeficientes da curva do sistema
            pump_data: Dados da bomba selecionada
            flow_values: Valores de vazão para plotagem
            n_bombas: Número de bombas em paralelo
            npsh_disponivel: NPSH disponível do sistema
            is_new_system: Indica se é um novo cálculo do sistema
        """
        try:
            # Proteção adicional: Se não for um novo sistema e já temos a escala definida, apenas ajustar gráficos secundários
            if not is_new_system and self.head_scale_set:
                logging.info("Mantendo escalas existentes para o gráfico Head (não é um novo sistema)")
                
                # Apenas ajustar os eixos Y dos gráficos secundários se houver dados de bomba
                if pump_data is not None:
                    self.adjust_secondary_graphs_y_scales(pump_data, npsh_disponivel)
                
                return  # Sair da função sem alterar outras escalas
            
            # Se for um novo sistema ou a escala do Head ainda não foi definida, ajustar todas as escalas
            if is_new_system or not self.head_scale_set:
                if system_curve is not None and self.system_max_flow is not None and self.system_max_head is not None:
                    # Arredondamento para cima para obter limites "bonitos"
                    max_flow = self.system_max_flow
                    # Adicionar 10% de margem e arredondar para cima para o próximo múltiplo de 5
                    max_flow_with_margin = np.ceil((max_flow * 1.1) / 5) * 5
                    
                    # Dividir vazão máxima pelo número de bombas para plotagem
                    system_flow_range = [0, max_flow_with_margin / n_bombas]
                    self.system_flow_range = system_flow_range  # Armazenar para usar em todos os gráficos
                    
                    # Ajustar escala do eixo X para todos os gráficos usando o mesmo range
                    self.ax_head.set_xlim(*system_flow_range)
                    self.ax_npshr.set_xlim(*system_flow_range)
                    self.ax_power.set_xlim(*system_flow_range)
                    self.ax_eff.set_xlim(*system_flow_range)
                    
                    # Ajustar escala do eixo Y apenas para Head
                    max_head = self.system_max_head
                    # Adicionar 10% de margem e arredondar para cima para o próximo múltiplo de 5
                    max_head_with_margin = np.ceil((max_head * 1.1) / 5) * 5
                    self.ax_head.set_ylim(0, max_head_with_margin)
                    
                    # Marcar que a escala do Head já foi definida
                    self.head_scale_set = True
                    
                    logging.info(f"Escala definida para todos os gráficos: X=[0, {system_flow_range[1]:.2f}], Head Y=[0, {max_head_with_margin:.2f}]")
                    
                    # Ajustar os gráficos secundários também
                    if pump_data is not None:
                        self.adjust_secondary_graphs_y_scales(pump_data, npsh_disponivel)
            else:
                # Este caso não deveria ocorrer devido ao retorno antecipado acima
                logging.warning("Condição não esperada no ajuste de escalas")
                    
        except Exception as e:
            logging.error(f"Erro ao ajustar escalas dos gráficos: {e}", exc_info=True)


    
    def adjust_secondary_graphs_y_scales(self, pump_data, npsh_disponivel):
        """
        Ajusta apenas os eixos Y dos gráficos secundários (NPSHr, Potência, Eficiência).
        """
        if self.system_flow_range is None:
            logging.warning("Range do sistema não definido para ajustar escalas Y secundárias")
            return
            
        # Ajuste do gráfico de NPSHr (apenas eixo Y)
        npshr_coef = pump_data.get('pump_coef_npshr')
        if npshr_coef is not None:
            self.adjust_y_scale_only(
                self.ax_npshr, 
                npshr_coef, 
                self.system_flow_range[0], 
                self.system_flow_range[1], 
                npsh_disponivel,
                "NPSHr"
            )
        
        # Ajuste do gráfico de Potência (apenas eixo Y)
        power_coef = pump_data.get('pump_coef_power')
        if power_coef is not None:
            self.adjust_y_scale_only(
                self.ax_power, 
                power_coef, 
                self.system_flow_range[0], 
                self.system_flow_range[1], 
                None,
                "Potência"
            )
        
        # Ajuste do gráfico de Eficiência (apenas eixo Y)
        eff_coef = pump_data.get('pump_coef_eff')
        if eff_coef is not None:
            self.adjust_y_scale_only(
                self.ax_eff, 
                eff_coef, 
                self.system_flow_range[0], 
                self.system_flow_range[1], 
                None,
                "Eficiência",
                max_y_limit=100  # Eficiência nunca ultrapassa 100%
            )
    
    def adjust_y_scale_only(self, ax, coef, min_flow, max_flow, reference_value=None, component_name="", max_y_limit=None):
        """
        Ajusta apenas a escala do eixo Y de um componente específico do gráfico.
        
        Parâmetros:
            ax: Eixo do matplotlib a ser ajustado
            coef: Coeficientes da curva
            min_flow: Vazão mínima do range do sistema
            max_flow: Vazão máxima do range do sistema
            reference_value: Valor de referência (ex: NPSH disponível)
            component_name: Nome do componente para logging
            max_y_limit: Limite máximo forçado para o eixo Y (opcional)
        """
        try:
            if coef is None:
                return
                
            # Calcular o valor máximo da curva para ajustar o eixo Y
            flow_values = np.linspace(min_flow, max_flow, 100)
            y_values = np.polyval(coef, flow_values)
            max_y = np.max(y_values)
            
            # Se tiver um valor de referência (ex: NPSH disponível), incluir na escala
            if reference_value is not None:
                max_y = max(max_y, reference_value)
            
            # Adicionar margem e arredondar para cima
            max_y_with_margin = np.ceil((max_y * 1.1) / 5) * 5
            
            # Se há um limite máximo definido, usá-lo
            if max_y_limit is not None and max_y_with_margin > max_y_limit:
                max_y_with_margin = max_y_limit
            
            # Ajustar apenas o eixo Y, mantendo o eixo X inalterado
            ax.set_ylim(0, max_y_with_margin)
            logging.info(f"Ajustando apenas eixo Y do gráfico de {component_name}: Y=0-{max_y_with_margin:.2f}")
            
        except Exception as e:
            logging.error(f"Erro ao ajustar escala Y do componente {component_name}: {e}", exc_info=True)
    
    def plot_system_curve(self, system_curve: np.ndarray, flow_values: np.ndarray, n_bombas: int, is_new_system: bool):
        """
        Plota a curva do sistema no gráfico de Head.
        
        Parâmetros:
            system_curve (numpy.ndarray): Coeficientes da curva do sistema
            flow_values (numpy.ndarray): Valores de vazão para plotagem
            n_bombas (int): Número de bombas em paralelo
            is_new_system (bool): Indica se é um novo cálculo do sistema
        """
        try:
            if system_curve is None or len(system_curve) == 0:
                logging.warning("Coeficientes da curva do sistema vazios ou inválidos")
                return
                
            # Gerar vazões para o eixo X
            system_flow_values = np.linspace(0.001, max(flow_values) * 1.1, 500)
            
            # Calcular heads para a curva do sistema
            system_head_values = np.polyval(system_curve, system_flow_values)
            
            # Armazenar os valores máximos para ajuste de escala (apenas se for um novo sistema)
            if is_new_system:
                self.system_max_flow = max(system_flow_values)
                self.system_max_head = max(system_head_values)
                logging.info(f"Novos valores máximos do sistema: Vazão={self.system_max_flow:.2f}, Head={self.system_max_head:.2f}")
            
            # Dividir vazões pelo número de bombas para plotagem
            system_flow_values_ajustado = system_flow_values / n_bombas
            
            # Plotar curva do sistema
            self.system_head_line = self.ax_head.plot(system_flow_values_ajustado, system_head_values, 
                         linestyle='-', color='blue', linewidth=2, 
                         label='Curva do Sistema')[0]
            
            # Configurar título com informação de bombas
            suffix = 's' if n_bombas > 1 else ''
            self.ax_head.set_title(f"Curva do Sistema x Curva da Bomba ({n_bombas} bomba{suffix} em paralelo)")
            self.ax_head.legend(loc='best')
            
            logging.info(f"Curva do sistema plotada com sucesso. Vazão máx: {max(system_flow_values_ajustado):.2f}, Head máx: {max(system_head_values):.2f}")
            
        except Exception as e:
            logging.error(f"Erro ao plotar curva do sistema: {e}", exc_info=True)
    
    def plot_npsh_disponivel(self, flow_values: np.ndarray, npsh_disponivel: float):
        """
        Plota a linha de NPSH disponível no gráfico de NPSH.
        
        Parâmetros:
            flow_values (numpy.ndarray): Valores de vazão para plotagem
            npsh_disponivel (float): NPSH disponível do sistema
        """
        try:
            if npsh_disponivel <= 0:
                logging.warning(f"NPSH disponível inválido: {npsh_disponivel}")
                return
                
            # Criar linha horizontal para NPSH disponível
            npsh_disp_values = np.full_like(flow_values, npsh_disponivel)
            self.system_npsh_line = self.ax_npshr.plot(flow_values, npsh_disp_values, 
                          linestyle='-', color='blue', linewidth=2, 
                          label='NPSH disponível')[0]
            
            self.ax_npshr.legend(loc='best')
            logging.info(f"NPSH disponível plotado: {npsh_disponivel:.2f} m")
            
        except Exception as e:
            logging.error(f"Erro ao plotar NPSH disponível: {e}", exc_info=True)
    
    def plot_pump_curves(self, pump_data: Dict[str, Any], flow_values: np.ndarray, 
                      intersection_point: Optional[List], npsh_disponivel: Optional[float]):
        """
        Plota as curvas da bomba em todos os gráficos.
        
        Parâmetros:
            pump_data (dict): Dados da bomba
            flow_values (numpy.ndarray): Valores de vazão para plotagem
            intersection_point (list): Ponto de interseção [vazão, head]
            npsh_disponivel (float): NPSH disponível do sistema
        """
        try:
            # Extrair dados da bomba
            pump_head_coef = pump_data.get('pump_coef_head')
            pump_npshr_coef = pump_data.get('pump_coef_npshr')
            pump_power_coef = pump_data.get('pump_coef_power')
            pump_eff_coef = pump_data.get('pump_coef_eff')
            pump_vazao_min = pump_data.get('pump_vazao_min', 0)
            pump_vazao_max = pump_data.get('pump_vazao_max', 100)
            
            # Registrar log para depuração
            logging.info(f"Plotando curvas da bomba. Vazão min: {pump_vazao_min}, Vazão máx: {pump_vazao_max}")
            logging.info(f"Coeficientes disponíveis: Head={pump_head_coef is not None}, "
                        f"NPSHr={pump_npshr_coef is not None}, "
                        f"Power={pump_power_coef is not None}, "
                        f"Eff={pump_eff_coef is not None}")
            
            # Usar o range do sistema para plotar as curvas da bomba
            if self.system_flow_range:
                min_flow = self.system_flow_range[0]
                max_flow = self.system_flow_range[1]
                pump_flow_values = np.linspace(min_flow, max_flow, 500)
                logging.info(f"Usando range do sistema para plotar curvas: [{min_flow:.2f}, {max_flow:.2f}]")
            else:
                # Fallback se não tivermos o range do sistema
                pump_flow_values = np.linspace(pump_vazao_min, pump_vazao_max, 500)
                logging.info(f"Usando range da bomba para plotar curvas: [{pump_vazao_min:.2f}, {pump_vazao_max:.2f}]")
            
            # Plotar cada curva em seu respectivo gráfico
            self.plot_head_curve(pump_head_coef, pump_flow_values, intersection_point)
            self.plot_npshr_curve(pump_npshr_coef, pump_flow_values, intersection_point, npsh_disponivel)
            self.plot_power_curve(pump_power_coef, pump_flow_values, intersection_point)
            self.plot_eff_curve(pump_eff_coef, pump_flow_values, intersection_point)
            
        except Exception as e:
            logging.error(f"Erro ao plotar curvas da bomba: {e}", exc_info=True)
    
    def plot_head_curve(self, pump_head_coef: np.ndarray, pump_flow_values: np.ndarray, 
                      intersection_point: Optional[List]):
        """Plota a curva de Head da bomba e o ponto de interseção."""
        if pump_head_coef is None or len(pump_head_coef) == 0:
            logging.warning("Coeficientes de Head da bomba vazios ou inválidos")
            return
            
        try:
            # Calcular valores de Head
            pump_head_values = np.polyval(pump_head_coef, pump_flow_values)
            
            # Plotar curva de Head
            self.ax_head.plot(pump_flow_values, pump_head_values, 
                         linestyle='--', color='green', linewidth=2, 
                         label='Curva da Bomba')
            
            # Plotar ponto de interseção
            if intersection_point is not None and len(intersection_point) >= 2:
                x, y = intersection_point[0], intersection_point[1]
                
                # Marcar o ponto de interseção
                self.ax_head.plot(x, y, 'ro', markersize=8, label='Ponto de Operação')
                
                # Adicionar linhas tracejadas até os eixos
                self.ax_head.axhline(y=y, color='r', linestyle=':', alpha=0.5)
                self.ax_head.axvline(x=x, color='r', linestyle=':', alpha=0.5)
                
                # Adicionar texto com o valor do ponto
                self.ax_head.annotate(f'({x:.1f}, {y:.1f})', 
                                 xy=(x, y), 
                                 xytext=(10, 10),
                                 textcoords='offset points',
                                 bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
                
                logging.info(f"Ponto de interseção plotado: ({x:.2f}, {y:.2f})")
            
            self.ax_head.legend(loc='best')
            
        except Exception as e:
            logging.error(f"Erro ao plotar curva de Head: {e}", exc_info=True)
    
    def plot_npshr_curve(self, pump_npshr_coef: np.ndarray, pump_flow_values: np.ndarray,
                       intersection_point: Optional[List], npsh_disponivel: Optional[float]):
        """
        Plota a curva de NPSHr da bomba e o NPSH disponível.
        
        Parâmetros:
            pump_npshr_coef (numpy.ndarray): Coeficientes da curva de NPSHr
            pump_flow_values (numpy.ndarray): Valores de vazão para plotagem
            intersection_point (list): Ponto de interseção [vazão, head]
            npsh_disponivel (float): NPSH disponível do sistema
        """
        if pump_npshr_coef is None or len(pump_npshr_coef) == 0:
            logging.warning("Coeficientes de NPSHr da bomba vazios ou inválidos")
            return
            
        try:
            # Calcular valores de NPSHr
            pump_npshr_values = np.polyval(pump_npshr_coef, pump_flow_values)
            
            # Plotar curva de NPSHr
            self.ax_npshr.plot(pump_flow_values, pump_npshr_values, 
                          linestyle='-', color='red', linewidth=2, 
                          label='NPSHr')
            
            # Plotar NPSH disponível
            if npsh_disponivel is not None and npsh_disponivel > 0:
                # Se tivermos o ponto de interseção, marcar o ponto correspondente na curva de NPSH
                if intersection_point is not None and len(intersection_point) >= 2:
                    x = intersection_point[0]  # Vazão do ponto de operação
                    
                    # Marcar ponto na curva do NPSH disponível
                    self.ax_npshr.plot(x, npsh_disponivel, 'bo', markersize=8, 
                                  label='NPSH disp. no ponto de operação')
                    
                    # Calcular NPSHr no ponto de operação
                    npshr_value = np.polyval(pump_npshr_coef, x)
                    
                    # Marcar ponto na curva do NPSHr
                    self.ax_npshr.plot(x, npshr_value, 'ro', markersize=8,
                                  label='NPSHr no ponto de operação')
                    
                    # Adicionar linhas tracejadas
                    self.ax_npshr.axvline(x=x, color='gray', linestyle=':', alpha=0.5)
                    
                    # Adicionar anotação com valores
                    margin = npsh_disponivel - npshr_value
                    self.ax_npshr.annotate(f'Margem: {margin:.1f} m', 
                                      xy=(x, (npsh_disponivel + npshr_value)/2), 
                                      xytext=(10, 0),
                                      textcoords='offset points',
                                      bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
                    
                    logging.info(f"Pontos de NPSHr/NPSH disp. plotados: NPSHr={npshr_value:.2f}, NPSH disp.={npsh_disponivel:.2f}, Margem={margin:.2f}")
            
            self.ax_npshr.legend(loc='best')
            
        except Exception as e:
            logging.error(f"Erro ao plotar curva de NPSHr: {e}", exc_info=True)
    
    def plot_power_curve(self, pump_power_coef: np.ndarray, pump_flow_values: np.ndarray,
                       intersection_point: Optional[List]):
        """Plota a curva de Potência da bomba e o ponto de operação."""
        if pump_power_coef is None or len(pump_power_coef) == 0:
            logging.warning("Coeficientes de Potência da bomba vazios ou inválidos")
            return
            
        try:
            # Calcular valores de Potência
            pump_power_values = np.polyval(pump_power_coef, pump_flow_values)
            
            # Plotar curva de Potência
            self.ax_power.plot(pump_flow_values, pump_power_values, 
                          linestyle='-', color='purple', linewidth=2, 
                          label='Potência')
            
            # Marcar ponto de operação
            if intersection_point is not None and len(intersection_point) >= 2:
                x = intersection_point[0]  # Vazão do ponto de operação
                power_value = np.polyval(pump_power_coef, x)
                
                # Marcar ponto na curva de potência
                self.ax_power.plot(x, power_value, 'ro', markersize=8, 
                              label='Ponto de operação')
                
                # Adicionar linhas tracejadas
                self.ax_power.axvline(x=x, color='gray', linestyle=':', alpha=0.5)
                
                # Adicionar anotação com valor
                self.ax_power.annotate(f'({x:.1f}, {power_value:.1f} cv)', 
                                  xy=(x, power_value), 
                                  xytext=(10, 10),
                                  textcoords='offset points',
                                  bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
                
                logging.info(f"Ponto de operação na curva de potência: ({x:.2f}, {power_value:.2f})")
            
            self.ax_power.legend(loc='best')
            
        except Exception as e:
            logging.error(f"Erro ao plotar curva de Potência: {e}", exc_info=True)
    
    def plot_eff_curve(self, pump_eff_coef: np.ndarray, pump_flow_values: np.ndarray,
                      intersection_point: Optional[List]):
        """Plota a curva de Eficiência da bomba e o ponto de operação."""
        if pump_eff_coef is None or len(pump_eff_coef) == 0:
            logging.warning("Coeficientes de Eficiência da bomba vazios ou inválidos")
            return
            
        try:
            # Calcular valores de Eficiência
            pump_eff_values = np.polyval(pump_eff_coef, pump_flow_values)
            
            # Plotar curva de Eficiência
            self.ax_eff.plot(pump_flow_values, pump_eff_values, 
                        linestyle='-', color='green', linewidth=2, 
                        label='Eficiência')
            
            # Marcar ponto de operação
            if intersection_point is not None and len(intersection_point) >= 2:
                x = intersection_point[0]  # Vazão do ponto de operação
                eff_value = np.polyval(pump_eff_coef, x)
                
                # Marcar ponto na curva de eficiência
                self.ax_eff.plot(x, eff_value, 'ro', markersize=8, 
                            label='Ponto de operação')
                
                # Adicionar linhas tracejadas
                self.ax_eff.axvline(x=x, color='gray', linestyle=':', alpha=0.5)
                
                # Adicionar anotação com valor
                self.ax_eff.annotate(f'({x:.1f}, {eff_value:.1f}%)', 
                                xy=(x, eff_value), 
                                xytext=(10, 10),
                                textcoords='offset points',
                                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
                
                logging.info(f"Ponto de operação na curva de eficiência: ({x:.2f}, {eff_value:.2f})")
            
            self.ax_eff.legend(loc='best')
            
        except Exception as e:
            logging.error(f"Erro ao plotar curva de Eficiência: {e}", exc_info=True)