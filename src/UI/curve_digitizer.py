from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, 
    QGroupBox, QFormLayout, QDoubleSpinBox, QMessageBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox, QComboBox,
    QApplication, QDialog, QRadioButton, QButtonGroup, QScrollArea, QLineEdit
)
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QPen, QImage, QTransform, 
    QCursor, QFont, QAction
)
from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF, QSize, pyqtSignal
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView
import numpy as np
import math
import os
import pandas as pd
from typing import List, Tuple, Dict, Optional, Any


class CurveDigitizerWidget(QWidget):
    """
    Widget principal para digitalização de curvas.
    Permite ao usuário carregar uma imagem, calibrar eixos, e extrair pontos de curvas.
    """
    # Sinal emitido quando os pontos de uma curva são extraídos
    curveExtracted = pyqtSignal(pd.DataFrame)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Digitalizador de Curvas")
        
        # Variáveis de estado
        self.image_path = None
        self.pixmap = None
        self.calibration_points = []
        self.curve_points = []
        self.x_min = 0.0
        self.x_max = 100.0
        self.y_min = 0.0
        self.y_max = 100.0
        self.current_mode = "calibration"  # calibration ou extraction
        self.current_curve_type = "head"  # head, efficiency, npshr
        self.zoom_factor = 1.0
        
        # Configurar a interface
        self.init_ui()
    
    def init_ui(self):
        """Inicializa os componentes da interface do usuário."""
        main_layout = QHBoxLayout(self)
        
        # Painel Esquerdo: Controles e Tabela de Pontos
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Grupo para carregar imagem
        load_group = QGroupBox("Carregar Imagem")
        load_layout = QVBoxLayout(load_group)
        self.load_button = QPushButton("Abrir Imagem")
        self.load_button.clicked.connect(self.load_image)
        load_layout.addWidget(self.load_button)
        
        self.load_pdf_button = QPushButton("Abrir PDF")
        self.load_pdf_button.clicked.connect(self.load_pdf)
        load_layout.addWidget(self.load_pdf_button)
        
        left_layout.addWidget(load_group)
        
        # Grupo para calibração
        calibration_group = QGroupBox("Calibração dos Eixos")
        calibration_layout = QFormLayout(calibration_group)
        
        self.x_min_input = QDoubleSpinBox()
        self.x_min_input.setRange(-1000, 1000)
        self.x_min_input.setValue(0.0)
        calibration_layout.addRow("X Mínimo:", self.x_min_input)
        
        self.x_max_input = QDoubleSpinBox()
        self.x_max_input.setRange(-1000, 1000)
        self.x_max_input.setValue(100.0)
        calibration_layout.addRow("X Máximo:", self.x_max_input)
        
        self.y_min_input = QDoubleSpinBox()
        self.y_min_input.setRange(-1000, 1000)
        self.y_min_input.setValue(0.0)
        calibration_layout.addRow("Y Mínimo:", self.y_min_input)
        
        self.y_max_input = QDoubleSpinBox()
        self.y_max_input.setRange(-1000, 1000)
        self.y_max_input.setValue(100.0)
        calibration_layout.addRow("Y Máximo:", self.y_max_input)
        
        self.calibrate_btn = QPushButton("Iniciar Calibração")
        self.calibrate_btn.clicked.connect(self.start_calibration)
        calibration_layout.addRow(self.calibrate_btn)
        
        self.calibration_status = QLabel("Status: Aguardando imagem")
        calibration_layout.addRow(self.calibration_status)
        
        left_layout.addWidget(calibration_group)
        
        # Grupo para extração de pontos
        extraction_group = QGroupBox("Extração de Pontos")
        extraction_layout = QVBoxLayout(extraction_group)
        
        curve_type_layout = QHBoxLayout()
        self.curve_type_label = QLabel("Tipo de Curva:")
        self.curve_type_combo = QComboBox()
        self.curve_type_combo.addItems(["Head (Altura)", "Eficiência", "NPSHr", "Potência"])
        self.curve_type_combo.currentIndexChanged.connect(self.change_curve_type)
        curve_type_layout.addWidget(self.curve_type_label)
        curve_type_layout.addWidget(self.curve_type_combo)
        extraction_layout.addLayout(curve_type_layout)
        
        self.extract_btn = QPushButton("Iniciar Extração de Pontos")
        self.extract_btn.clicked.connect(self.start_extraction)
        self.extract_btn.setEnabled(False)
        extraction_layout.addWidget(self.extract_btn)
        
        self.clear_points_btn = QPushButton("Limpar Pontos")
        self.clear_points_btn.clicked.connect(self.clear_points)
        self.clear_points_btn.setEnabled(False)
        extraction_layout.addWidget(self.clear_points_btn)
        
        self.extraction_status = QLabel("Status: Calibre os eixos primeiro")
        extraction_layout.addWidget(self.extraction_status)
        
        left_layout.addWidget(extraction_group)
        
        # Tabela de pontos extraídos
        points_group = QGroupBox("Pontos Extraídos")
        points_layout = QVBoxLayout(points_group)
        
        self.points_table = QTableWidget(0, 2)
        self.points_table.setHorizontalHeaderLabels(["Vazão (m³/h)", "Head (m)"])
        self.points_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        points_layout.addWidget(self.points_table)
        
        self.export_btn = QPushButton("Exportar para Curva de Bomba")
        self.export_btn.clicked.connect(self.export_points)
        self.export_btn.setEnabled(False)
        points_layout.addWidget(self.export_btn)
        
        left_layout.addWidget(points_group)
        
        # Botões para ajustar visualização
        zoom_group = QGroupBox("Visualização")
        zoom_layout = QHBoxLayout(zoom_group)
        
        self.zoom_in_btn = QPushButton("Zoom In (+)")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(self.zoom_in_btn)
        
        self.zoom_out_btn = QPushButton("Zoom Out (-)")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(self.zoom_out_btn)
        
        self.reset_zoom_btn = QPushButton("Reset Zoom")
        self.reset_zoom_btn.clicked.connect(self.reset_zoom)
        zoom_layout.addWidget(self.reset_zoom_btn)
        
        left_layout.addWidget(zoom_group)
        
        # Painel Direito: Visualização da Imagem
        image_panel = QScrollArea()
        image_panel.setWidgetResizable(True)
        
        self.image_view = ImageViewWidget(self)
        image_panel.setWidget(self.image_view)
        
        # Conecta sinais do visualizador de imagem
        self.image_view.pointSelected.connect(self.handle_point_selection)
        
        # Configuração final do layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(image_panel, 3)
        
        # Inicializar dimensões da janela
        self.resize(1200, 800)
    
    def load_image(self):
        """Carrega uma imagem de arquivo JPG ou PNG."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Imagem", "", "Imagens (*.jpg *.jpeg *.png *.bmp)"
        )
        
        if file_path:
            self.image_path = file_path
            self.pixmap = QPixmap(file_path)
            
            if self.pixmap.isNull():
                QMessageBox.critical(self, "Erro", "Não foi possível carregar a imagem.")
                return
            
            self.image_view.set_image(self.pixmap)
            self.calibration_status.setText("Status: Imagem carregada. Defina os valores dos eixos e inicie a calibração.")
            self.reset_data()
    
    def load_pdf(self):
        """Carrega uma página de um arquivo PDF."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir PDF", "", "Arquivos PDF (*.pdf)"
        )
        
        if file_path:
            dialog = PDFPageSelectorDialog(file_path, self)
            if dialog.exec():
                selected_page = dialog.get_selected_page()
                
                # Converter a página do PDF em uma imagem
                pdf_document = QPdfDocument()
                pdf_document.load(file_path)
                
                if pdf_document.pageCount() > 0 and selected_page < pdf_document.pageCount():
                    page = pdf_document.page(selected_page)
                    if page:
                        # Renderizar a página como imagem
                        size = page.pageSize().toSize()
                        image = QImage(size, QImage.Format.Format_ARGB32)
                        image.fill(Qt.GlobalColor.white)
                        
                        painter = QPainter(image)
                        page.render(painter, QRectF(0, 0, size.width(), size.height()))
                        painter.end()
                        
                        # Converter para QPixmap e exibir
                        self.pixmap = QPixmap.fromImage(image)
                        self.image_view.set_image(self.pixmap)
                        self.image_path = f"{file_path} (Página {selected_page+1})"
                        self.calibration_status.setText("Status: PDF carregado. Defina os valores dos eixos e inicie a calibração.")
                        self.reset_data()
    
    def reset_data(self):
        """Reinicia os dados após carregar uma nova imagem."""
        self.calibration_points = []
        self.curve_points = []
        self.current_mode = "calibration"
        self.clear_points_table()
        self.calibrate_btn.setEnabled(True)
        self.extract_btn.setEnabled(False)
        self.clear_points_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
    
    def start_calibration(self):
        """Inicia o modo de calibração para marcar os pontos de referência."""
        if not self.pixmap:
            QMessageBox.warning(self, "Aviso", "Carregue uma imagem antes de calibrar.")
            return
        
        # Atualizar valores de calibração
        self.x_min = self.x_min_input.value()
        self.x_max = self.x_max_input.value()
        self.y_min = self.y_min_input.value()
        self.y_max = self.y_max_input.value()
        
        if self.x_min >= self.x_max or self.y_min >= self.y_max:
            QMessageBox.warning(self, "Aviso", "Os valores máximos devem ser maiores que os mínimos.")
            return
        
        self.calibration_points = []
        self.current_mode = "calibration"
        
        # Instruções na interface
        self.calibration_status.setText("Clique nos 4 pontos de calibração na ordem: "
                                       "(Xmin,Ymin), (Xmax,Ymin), (Xmax,Ymax), (Xmin,Ymax)")
        
        # Configurar o visualizador de imagem para o modo de calibração
        self.image_view.set_mode("calibration")
    
    def start_extraction(self):
        """Inicia o modo de extração de pontos."""
        if len(self.calibration_points) != 4:
            QMessageBox.warning(self, "Aviso", "Complete a calibração primeiro (4 pontos).")
            return
        
        self.curve_points = []
        self.current_mode = "extraction"
        self.clear_points_table()
        
        # Atualizar tipo de curva
        self.change_curve_type()
        
        # Configurar o visualizador de imagem para o modo de extração
        self.image_view.set_mode("extraction")
        
        self.extraction_status.setText("Clique nos pontos da curva. Começando do menor para o maior valor de vazão.")
        self.clear_points_btn.setEnabled(True)
    
    def handle_point_selection(self, point: QPoint):
        """Processa um ponto selecionado pelo usuário na imagem."""
        if self.current_mode == "calibration":
            # Adicionar ponto de calibração
            self.calibration_points.append(point)
            
            # Atualizar mensagem de status
            remaining = 4 - len(self.calibration_points)
            if remaining > 0:
                self.calibration_status.setText(f"Faltam {remaining} pontos de calibração.")
            else:
                self.calibration_status.setText("Calibração concluída! Você pode iniciar a extração de pontos.")
                self.extract_btn.setEnabled(True)
                
        elif self.current_mode == "extraction":
            # Converter o ponto da imagem para coordenadas reais
            real_point = self.image_to_real_coordinates(point)
            
            # Adicionar à lista de pontos da curva
            self.curve_points.append(real_point)
            
            # Atualizar a tabela de pontos
            self.update_points_table()
            
            # Habilitar exportação quando houver pontos suficientes
            self.export_btn.setEnabled(len(self.curve_points) >= 3)
            
            # Atualizar visualização
            self.image_view.curve_points = self.curve_points
            self.image_view.repaint()
    
    def change_curve_type(self):
        """Muda o tipo de curva que está sendo extraída."""
        curve_type_index = self.curve_type_combo.currentIndex()
        
        if curve_type_index == 0:  # Head
            self.current_curve_type = "head"
            self.points_table.setHorizontalHeaderLabels(["Vazão (m³/h)", "Head (m)"])
        elif curve_type_index == 1:  # Eficiência
            self.current_curve_type = "efficiency"
            self.points_table.setHorizontalHeaderLabels(["Vazão (m³/h)", "Eficiência (%)"])
        elif curve_type_index == 2:  # NPSHr
            self.current_curve_type = "npshr"
            self.points_table.setHorizontalHeaderLabels(["Vazão (m³/h)", "NPSHr (m)"])
        elif curve_type_index == 3:  # Potência
            self.current_curve_type = "power"
            self.points_table.setHorizontalHeaderLabels(["Vazão (m³/h)", "Potência (cv)"])
        
        # Limpar pontos ao mudar o tipo de curva
        self.clear_points()
    
    def clear_points(self):
        """Limpa os pontos da curva atual."""
        self.curve_points = []
        self.clear_points_table()
        self.export_btn.setEnabled(False)
        self.image_view.curve_points = []
        self.image_view.repaint()
    
    def clear_points_table(self):
        """Limpa a tabela de pontos."""
        self.points_table.setRowCount(0)
    
    def update_points_table(self):
        """Atualiza a tabela de pontos com os valores atuais."""
        self.points_table.setRowCount(len(self.curve_points))
        
        for i, (x, y) in enumerate(self.curve_points):
            self.points_table.setItem(i, 0, QTableWidgetItem(f"{x:.2f}"))
            self.points_table.setItem(i, 1, QTableWidgetItem(f"{y:.2f}"))
    
    def image_to_real_coordinates(self, point: QPoint) -> Tuple[float, float]:
        """
        Converte coordenadas da imagem para coordenadas reais usando a calibração.
        Implementa uma transformação projetiva (perspectiva).
        """
        if len(self.calibration_points) != 4:
            return (0.0, 0.0)
        
        # Pontos de origem (pixels da imagem)
        src_points = np.array([
            [self.calibration_points[0].x(), self.calibration_points[0].y()],
            [self.calibration_points[1].x(), self.calibration_points[1].y()], 
            [self.calibration_points[2].x(), self.calibration_points[2].y()],
            [self.calibration_points[3].x(), self.calibration_points[3].y()]
        ], dtype=np.float32)
        
        # Pontos de destino (coordenadas reais)
        dst_points = np.array([
            [self.x_min, self.y_min],  # Esq Inf
            [self.x_max, self.y_min],  # Dir Inf
            [self.x_max, self.y_max],  # Dir Sup
            [self.x_min, self.y_max]   # Esq Sup
        ], dtype=np.float32)
        
        # Calcular a matriz de perspectiva
        try:
            # Método simplificado para cálculo da matriz de transformação usando mínimos quadrados
            # Isso é uma aproximação para uma transformação projetiva completa
            A = []
            b = []
            
            for i in range(4):
                src_x, src_y = src_points[i]
                dst_x, dst_y = dst_points[i]
                
                A.append([src_x, src_y, 1, 0, 0, 0, -dst_x*src_x, -dst_x*src_y])
                A.append([0, 0, 0, src_x, src_y, 1, -dst_y*src_x, -dst_y*src_y])
                
                b.append(dst_x)
                b.append(dst_y)
            
            A = np.array(A)
            b = np.array(b)
            
            # Resolver o sistema de equações
            h = np.linalg.lstsq(A, b, rcond=None)[0]
            H = np.array([
                [h[0], h[1], h[2]],
                [h[3], h[4], h[5]],
                [h[6], h[7], 1]
            ])
            
            # Aplicar a transformação ao ponto
            p = np.array([point.x(), point.y(), 1])
            p_transformed = H @ p
            
            # Normalizar
            p_transformed = p_transformed / p_transformed[2]
            
            return (p_transformed[0], p_transformed[1])
            
        except np.linalg.LinAlgError:
            QMessageBox.warning(self, "Erro", "Erro ao calcular transformação. Tente recalibrar.")
            return (0.0, 0.0)
    
    def export_points(self):
        """Exporta os pontos extraídos para um DataFrame pandas."""
        if len(self.curve_points) < 3:
            QMessageBox.warning(self, "Aviso", "São necessários pelo menos 3 pontos para exportar.")
            return
        
        # Organizar pontos por valor de x (vazão)
        sorted_points = sorted(self.curve_points, key=lambda p: p[0])
        
        # Extrair valores x e y
        x_values = [p[0] for p in sorted_points]
        y_values = [p[1] for p in sorted_points]
        
        # Criar DataFrame
        data = pd.DataFrame({
            'vazao': x_values,
            self.current_curve_type: y_values
        })
        
        # Emitir sinal com os dados
        self.curveExtracted.emit(data)
        
        # Abrir diálogo para definir parâmetros da bomba
        dialog = PumpDataDialog(data, self.current_curve_type, self)
        if dialog.exec():
            QMessageBox.information(self, "Sucesso", "Dados enviados para o módulo de seleção de bombas.")
    
    def zoom_in(self):
        """Aumenta o zoom da imagem."""
        self.zoom_factor *= 1.2
        self.image_view.set_zoom(self.zoom_factor)
    
    def zoom_out(self):
        """Diminui o zoom da imagem."""
        self.zoom_factor /= 1.2
        self.zoom_factor = max(0.1, self.zoom_factor)
        self.image_view.set_zoom(self.zoom_factor)
    
    def reset_zoom(self):
        """Restaura o zoom para o valor original."""
        self.zoom_factor = 1.0
        self.image_view.set_zoom(self.zoom_factor)


class ImageViewWidget(QWidget):
    """
    Widget para exibição de imagem e seleção de pontos.
    """
    # Sinal emitido quando um ponto é selecionado
    pointSelected = pyqtSignal(QPoint)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap = None
        self.mode = "calibration"  # calibration ou extraction
        self.calibration_points = []
        self.curve_points = []
        self.zoom_factor = 1.0
        self.offset = QPoint(0, 0)
        self.last_pos = None
        self.setMouseTracking(True)
        self.setMinimumSize(400, 300)
        
        # Habilitar eventos de mouse
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def set_image(self, pixmap):
        """Define a imagem a ser exibida."""
        self.pixmap = pixmap
        self.calibration_points = []
        self.curve_points = []
        self.offset = QPoint(0, 0)
        self.update()
    
    def set_mode(self, mode):
        """Define o modo de operação (calibration ou extraction)."""
        self.mode = mode
        self.update()
    
    def set_zoom(self, factor):
        """Define o fator de zoom."""
        self.zoom_factor = factor
        self.update()
    
    def paintEvent(self, event):
        """Desenha a imagem e os pontos marcados."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Desenhar fundo
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        
        if not self.pixmap:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Nenhuma imagem carregada")
            return
        
        # Aplicar zoom e deslocamento
        painter.translate(self.offset)
        painter.scale(self.zoom_factor, self.zoom_factor)
        
        # Desenhar a imagem
        painter.drawPixmap(0, 0, self.pixmap)
        
        # Desenhar os pontos de calibração
        painter.setPen(QPen(QColor(255, 0, 0), 2 / self.zoom_factor))
        for i, point in enumerate(self.calibration_points):
            # Desenhar círculo
            radius = 5 / self.zoom_factor
            painter.drawEllipse(point, radius, radius)
            
            # Desenhar número do ponto
            font = QFont()
            font.setPointSizeF(10 / self.zoom_factor)
            painter.setFont(font)
            painter.drawText(point + QPoint(10 / self.zoom_factor, 10 / self.zoom_factor), str(i+1))
        
        # Desenhar retângulo de calibração se todos os pontos estiverem marcados
        if len(self.calibration_points) == 4:
            painter.setPen(QPen(QColor(0, 0, 255, 128), 1 / self.zoom_factor))
            points = [QPointF(p.x(), p.y()) for p in self.calibration_points]
            painter.drawLine(points[0], points[1])
            painter.drawLine(points[1], points[2])
            painter.drawLine(points[2], points[3])
            painter.drawLine(points[3], points[0])
        
        # Desenhar os pontos da curva
        if self.mode == "extraction" and hasattr(self.parent(), "image_to_real_coordinates"):
            painter.setPen(QPen(QColor(0, 128, 0), 2 / self.zoom_factor))
            
            # Desenhar pontos
            for i, point in enumerate(self.curve_points):
                # Converter de coordenadas reais para coordenadas da imagem
                img_point = self.real_to_image_coordinates(point)
                radius = 3 / self.zoom_factor
                painter.drawEllipse(img_point, radius, radius)
                
                # Desenhar valor
                font = QFont()
                font.setPointSizeF(8 / self.zoom_factor)
                painter.setFont(font)
                painter.drawText(img_point + QPoint(6 / self.zoom_factor, 6 / self.zoom_factor),
                                f"({point[0]:.1f}, {point[1]:.1f})")
            
            # Desenhar linha conectando os pontos
            if len(self.curve_points) > 1:
                painter.setPen(QPen(QColor(0, 128, 0, 180), 1 / self.zoom_factor))
                for i in range(len(self.curve_points) - 1):
                    img_point1 = self.real_to_image_coordinates(self.curve_points[i])
                    img_point2 = self.real_to_image_coordinates(self.curve_points[i + 1])
                    painter.drawLine(img_point1, img_point2)
    
    def mousePressEvent(self, event):
        """Captura cliques do mouse para seleção de pontos ou pan da imagem."""
        if not self.pixmap:
            return
        
        if event.button() == Qt.MouseButton.LeftButton:
            # Calcular a posição real na imagem considerando zoom e deslocamento
            pos = (event.position().toPoint() - self.offset) / self.zoom_factor
            
            # Se na área válida da imagem
            if pos.x() >= 0 and pos.y() >= 0 and pos.x() < self.pixmap.width() and pos.y() < self.pixmap.height():
                if self.mode == "calibration":
                    if len(self.parent().calibration_points) < 4:
                        # Adicionar ponto de calibração
                        self.parent().calibration_points.append(QPoint(int(pos.x()), int(pos.y())))
                        self.calibration_points = self.parent().calibration_points
                        self.pointSelected.emit(QPoint(int(pos.x()), int(pos.y())))
                        self.update()
                elif self.mode == "extraction":
                    # Adicionar ponto à curva
                    self.pointSelected.emit(QPoint(int(pos.x()), int(pos.y())))
                    self.update()
            
            # Salvar posição para pan
            self.last_pos = event.position().toPoint()
        
        elif event.button() == Qt.MouseButton.RightButton:
            # Pan com botão direito
            self.last_pos = event.position().toPoint()
    
    def mouseMoveEvent(self, event):
        """Atualiza o pan da imagem ao mover o mouse com botão pressionado."""
        if not self.pixmap:
            return
        
        if self.last_pos and event.buttons() & Qt.MouseButton.RightButton:
            # Calcular delta
            delta = event.position().toPoint() - self.last_pos
            self.offset += delta
            self.last_pos = event.position().toPoint()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Finaliza o pan da imagem."""
        self.last_pos = None
    
    def wheelEvent(self, event):
        """Permite zoom com a roda do mouse."""
        if not self.pixmap:
            return
        
        # Calcular novo zoom
        zoom_in = event.angleDelta().y() > 0
        
        if zoom_in:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor /= 1.1
            self.zoom_factor = max(0.1, self.zoom_factor)
        
        # Atualizar zoom no widget pai
        if hasattr(self.parent(), "zoom_factor"):
            self.parent().zoom_factor = self.zoom_factor
        
        self.update()
    
    def real_to_image_coordinates(self, real_point) -> QPoint:
        """
        Converte coordenadas reais para coordenadas da imagem usando a calibração.
        """
        if not hasattr(self.parent(), "calibration_points") or len(self.parent().calibration_points) != 4:
            return QPoint(0, 0)
        
        parent = self.parent()
        
        # Calcular a porcentagem do ponto no espaço real
        x_norm = (real_point[0] - parent.x_min) / (parent.x_max - parent.x_min)
        y_norm = (real_point[1] - parent.y_min) / (parent.y_max - parent.y_min)
        
        # Invertendo y porque no espaço real, y cresce para cima, mas na imagem cresce para baixo
        y_norm = 1 - y_norm
        
        # Interpolar nas coordenadas da imagem usando os pontos de calibração
        x_img = (1-x_norm) * (1-y_norm) * parent.calibration_points[0].x() + \
                x_norm * (1-y_norm) * parent.calibration_points[1].x() + \
                x_norm * y_norm * parent.calibration_points[2].x() + \
                (1-x_norm) * y_norm * parent.calibration_points[3].x()
        
        y_img = (1-x_norm) * (1-y_norm) * parent.calibration_points[0].y() + \
                x_norm * (1-y_norm) * parent.calibration_points[1].y() + \
                x_norm * y_norm * parent.calibration_points[2].y() + \
                (1-x_norm) * y_norm * parent.calibration_points[3].y()
        
        return QPoint(int(x_img), int(y_img))


class PDFPageSelectorDialog(QDialog):
    """
    Diálogo para selecionar uma página específica de um PDF.
    """
    def __init__(self, pdf_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selecionar Página do PDF")
        
        self.pdf_document = QPdfDocument()
        self.pdf_document.load(pdf_path)
        
        layout = QVBoxLayout(self)
        
        self.page_label = QLabel(f"Selecione uma página (1-{self.pdf_document.pageCount()}):")
        layout.addWidget(self.page_label)
        
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.setMaximum(max(1, self.pdf_document.pageCount()))
        layout.addWidget(self.page_spin)
        
        # Botões
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        # Ajustar tamanho
        self.setMinimumWidth(300)
    
    def get_selected_page(self):
        """Retorna o índice da página selecionada (base 0)."""
        return self.page_spin.value() - 1


class PumpDataDialog(QDialog):
    """
    Diálogo para definir os parâmetros adicionais da bomba ao exportar dados.
    """
    def __init__(self, data, curve_type, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Informações da Bomba")
        self.data = data
        self.curve_type = curve_type
        
        layout = QVBoxLayout(self)
        
        # Grupo de informações gerais
        info_group = QGroupBox("Informações da Bomba")
        info_layout = QFormLayout(info_group)
        
        self.marca_input = QLineEdit()
        info_layout.addRow("Marca:", self.marca_input)
        
        self.modelo_input = QLineEdit()
        info_layout.addRow("Modelo:", self.modelo_input)
        
        self.diametro_input = QSpinBox()
        self.diametro_input.setMinimum(1)
        self.diametro_input.setMaximum(1000)
        self.diametro_input.setValue(150)
        info_layout.addRow("Diâmetro do Rotor (mm):", self.diametro_input)
        
        self.rotacao_input = QSpinBox()
        self.rotacao_input.setMinimum(1)
        self.rotacao_input.setMaximum(10000)
        self.rotacao_input.setValue(3500)
        info_layout.addRow("Rotação (rpm):", self.rotacao_input)
        
        layout.addWidget(info_group)
        
        # Botões
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Salvar")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        # Ajustar tamanho
        self.setMinimumWidth(400)
    
    def accept(self):
        """Lógica ao aceitar o diálogo."""
        # Aqui você pode integrar com seu sistema de bombas
        # por exemplo, salvando os dados no banco de dados
        super().accept()


if __name__ == "__main__":
    app = QApplication([])
    widget = CurveDigitizerWidget()
    widget.show()
    app.exec()