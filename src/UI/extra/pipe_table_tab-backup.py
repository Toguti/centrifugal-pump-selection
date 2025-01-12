2# pipe_table_widget.py

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QLabel, QSpinBox, QDoubleSpinBox, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator
from UI.func.rotated_label import RotatedLabel
from UI.data.header_table_data import *
import pandas as pd

class PipeTableWidget(QTableWidget):
    def __init__(self, rows, columns, parent=None):
        super().__init__(rows, columns, parent)

        # Configure Header Row Span
        ## 2 Collums
        self.setSpan(0,0,2,1)
        self.setSpan(0,2,2,1)
        self.setSpan(0,3,2,1)
        self.setSpan(0,24,2,1)
        self.setSpan(0,25,2,1)
        ## 1 Columns
        self.setSpan(0,1,1,2)
        self.setSpan(0,4,1,20)
        self.setCellWidget(0,1,QLabel("Trecho"))
        self.setCellWidget(0,4,QLabel("Quantidades"))

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
            for col in range(3,self.columnCount()-1):
                cell_widget = self.cellWidget(row,col)
                row_data.append(cell_widget.value())
            data.append(row_data)

        return data
    
    # def get_max_flow_value(self):
    #     df = pd.DataFrame(self.retriveData())
    #     return df[1].max(skipna=True)
    

class SinglePathInput(QWidget):
    def __init__(self):
        super().__init__()
        
        # Main vertical layout
        self.main_layout = QHBoxLayout()
        
        # Create label
        self.label_vazao = QLabel("Vazão Nominal: ")
        self.field_vazao = QLineEdit()
        self.field_vazao.setValidator(QIntValidator())
        self.unit_vazao = QLabel("m³/h")
        self.main_layout.addWidget(self.label_vazao)
        self.main_layout.addWidget(self.field_vazao)
        self.main_layout.addWidget(self.unit_vazao)
        
        # Set the main layout to the widget
        self.setLayout(self.main_layout)
        self.setMaximumWidth(400)

    def get_flow_value(self):
        return self.field_vazao.text()
        