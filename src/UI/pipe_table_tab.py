# pipe_table_widget.py

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QLabel, QSpinBox, QDoubleSpinBox
from PyQt6.QtCore import Qt
from UI.func.rotated_label import RotatedLabel
from UI.data.header_table_data import *
import pandas as pd

class PipeTableWidget(QTableWidget):
    def __init__(self, rows, columns, parent=None):
        super().__init__(rows, columns, parent)

        # Configure Header Row Span
        ## 2 Collums
        self.setSpan(0,0,2,1)
        self.setSpan(0,3,2,1)
        self.setSpan(0,4,2,1)
        self.setSpan(0,24,2,1)
        self.setSpan(0,25,2,1)
        ## 1 Columns
        self.setSpan(0,1,1,2)
        self.setSpan(0,5,1,19)
        self.setCellWidget(0,1,QLabel("Trecho"))
        self.setCellWidget(0,5,QLabel("Quantidades"))

        for col, header in enumerate(header_second_line):
            self.setRotatedCell(1, col, header)

        self.setRowHeight(1,150)
        self.addRow()

        for col in range(0,self.columnCount()):
            if col == 4:
                self.setColumnWidth(col,50)
            elif col == 3:
                self.setColumnWidth(col,80)
            else:
                self.setColumnWidth(col,15)
            

    def setRotatedCell(self, row, column, text):
        rotated_label = RotatedLabel(text)
        self.setCellWidget(row, column, rotated_label)

    def addRow(self):
        row_position = self.rowCount()
        self.insertRow(row_position)
        
        for col in range(self.columnCount() - 1):  # Exclude the last column for the button
            if col==0:
                row_index = QLabel(str(row_position-1),alignment=Qt.AlignmentFlag.AlignHCenter)
                row_index.setAlignment(Qt.AlignmentFlag.AlignVCenter)
                self.setCellWidget(row_position,0,row_index)

            elif col == 1 or col == 2:
                cell_type = QSpinBox()
                cell_type.setButtonSymbols(cell_type.ButtonSymbols.NoButtons)
                self.setCellWidget(row_position,col,cell_type)

            elif col == 3:
                cell_type = QDoubleSpinBox()
                cell_type.setMaximum(9999999)
                cell_type.setDecimals(2)
                cell_type.setSuffix(" m³/h")
                cell_type.setButtonSymbols(cell_type.ButtonSymbols.NoButtons)
                if row_position != 2:
                    cell_type.setValue(self.cellWidget(row_position-1,col).value())
                self.setCellWidget(row_position,col,cell_type)

            elif col == 4:
                cell_type = QDoubleSpinBox()
                cell_type.setMaximum(9999999)
                cell_type.setDecimals(2)
                cell_type.setSuffix(" m")
                cell_type.setButtonSymbols(cell_type.ButtonSymbols.NoButtons)
                self.setCellWidget(row_position,col,cell_type)

            else:
                self.setCellWidget(row_position,col,QSpinBox())
            


        
        # Add remove button
        remove_button = QPushButton("Del")
        remove_button.clicked.connect(lambda ch, r=row_position: self.removeRow(r))
        self.setCellWidget(row_position, self.columnCount() - 1, remove_button)

    def retriveData(self):
        data = []
        for row in range(2,self.rowCount()):
            row_data = []
            for col in range(2,self.columnCount()-1):
                cell_widget = self.cellWidget(row,col)
                row_data.append(cell_widget.value())
            data.append(row_data)

        return data
    
    def get_max_flow_value(self):
        df = pd.DataFrame(self.retriveData())
        return df[1].max(skipna=True)
        







# import sys
# from PyQt6.QtWidgets import (QTableWidget, 
#                              QApplication, 
#                              QMainWindow, 
#                              QLabel, 
#                              QTableWidgetItem,
#                              QWidget)
# from PyQt6.QtGui import QPaintEvent, QPainter, QColor
# from PyQt6.QtCore import Qt, QSize


# class PressureLossTable(QTableWidget):
#     def __init__(self):
#         # Table size configuration

#         super().__init__(4,24)

#         # Table Interface Configuration
#         self.horizontalHeader().setVisible(False)

#         # Configure Header Row Span
#         self.setSpan(0,0,2,1)
#         self.setSpan(0,1,1,2)
#         self.setSpan(0,5,1,21)
#         self.setSpan(0,3,2,1)
#         self.setSpan(0,4,2,1)
       
#         # First Row
#         

#         # Second Row
#          # Set Items for Header
#         self.table_header_row_2 = ["Indice", "De", "Para", "Flow", "Trecho Retilíneo", 
#                                    "Cotovelo 90° Raio Longo", 
#                                    "Cotovelo 90° Raio Médio",
#                                    "Cotovelo 90° Raio Curto",
#                                    "Cotovelo 45°",
#                                    "Curva 90° Raio Longo",
#                                    "Curva 90° Raio Curto",
#                                    "Curva 45°",
#                                    "Entrada Normal",
#                                    "Entrada de Borda",
#                                    "Válvula Gaveta Aberta",
#                                    "Válvula Globo Aberta",
#                                    "Válvula Ângular Aberta",
#                                    "Passagem Reta Tê",
#                                    "Derivação Tê",
#                                    "Bifurcação Tê",
#                                    "Válvula de Pé e Crivo",
#                                    "Saída de Canalização",
#                                    "Válvula de Retenção Leve",
#                                    "Válvula de Retenção Pesado"]
#         for i, e in enumerate(self.table_header_row_2):
#             self.setCellWidget(1,i,QLabel(e))
        
        


#         self.show
    


# class Sheet(QMainWindow):
#     def __init__(self):
#         super().__init__()
        
#         self.form_widget = Pressure_loss_table()
#         self.setCentralWidget(self.form_widget)
#         self.setWindowTitle("Pressure Loss Calculator")
#         self.setMinimumSize(QSize(1024, 768))

#         self.show()


# app = QApplication(sys.argv)
# sheet = Sheet()
# sys.exit(app.exec())