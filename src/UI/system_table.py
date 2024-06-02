# my_table_widget.py

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton
from rotated_label import RotatedLabel

class MyTableWidget(QTableWidget):
    def __init__(self, rows, columns, parent=None):
        super().__init__(rows, columns, parent)

    def setRotatedCell(self, row, column, text):
        rotated_label = RotatedLabel(text)
        self.setCellWidget(row, column, rotated_label)

    def populateTableFromData(self, headers, data):
        # Set the headers horizontally
        for col, header in enumerate(headers):
            self.setHorizontalHeaderItem(col, QTableWidgetItem(header))

        # Populate the first row with vertical headers
        for col, header in enumerate(data[0]):
            self.setRotatedCell(0, col, header)

        # Populate the rest of the table with data
        for row in range(1, len(data)):
            for col in range(len(data[row])):
                item = QTableWidgetItem(data[row][col])
                self.setItem(row, col, item)

            # Add a remove button to each data row
            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(lambda ch, r=row: self.removeRow(r))
            self.setCellWidget(row, len(data[row]), remove_button)

        # Resize the first row height to fit the rotated text
        self.resizeRowToContents(0)

    def addRow(self):
        row_position = self.rowCount()
        self.insertRow(row_position)
        for col in range(self.columnCount() - 1):  # Exclude the last column for the button
            self.setItem(row_position, col, QTableWidgetItem(""))
        
        # Add remove button
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda ch, r=row_position: self.removeRow(r))
        self.setCellWidget(row_position, self.columnCount() - 1, remove_button)






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
#         self.setCellWidget(0,0,QLabel("Index"))
#         self.setCellWidget(0,1,QLabel("Trecho"))
#         self.setCellWidget(0,2,QLabel("Trecho"))
#         self.setCellWidget(0,5,QLabel("Quantidades"))

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