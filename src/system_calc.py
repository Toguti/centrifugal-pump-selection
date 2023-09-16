from PyQt6.QtCore import (Qt, 
                          QSize, 
                          QAbstractTableModel
                          )
from PyQt6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
    QComboBox,
    QPushButton,
    QGridLayout,
    QTableView,
    QLineEdit
)
import sys
from pressure_drop.local_loss import *


class InputTable(QAbstractTableModel):
    def __init__(self, data):
        super(InputTable, self).__init__()
        self._data = data

    def data (self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
        

    def rowCount(self, index):
        return len(self._data)
    
    def columnCount(self,index):
        return len(self._data[0])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()


        # Main window Layout
        self.setWindowTitle("Pressure Loss Calculator")
        self.setMinimumSize(QSize(600, 720))

        # User input widget
        user_input_layout = QGridLayout()
        user_input_layout.addWidget(QLabel("Index"),0,0)
        user_input_layout.addWidget(QLabel("Conexão"),0,1)
        user_input_layout.addWidget(QLabel("Quantidade"),0,2)
        user_input_layout.addWidget(QLabel("Diâmetro"),0,3)
        user_input_layout.addWidget(QLabel("Vazão"),0,4)

        self.path_index = QDoubleSpinBox()
        self.path_index.setValue(1)
        self.path_index.setMinimum(0)
        self.path_index.setDecimals(0)
        user_input_layout.addWidget(self.path_index,1,0)
        self.component_list = QComboBox()
        self.component_list.addItems(
            ['ct_90_rl', 
            'ct_90_rm', 
            'ct_90_rc', 
            'ct_45', 
            'cur_90_1_1-2', 
            'cur_90_1', 
            'cur_45', 
            'ent_norm', 
            'ent_borda', 
            'rg_ga_a', 
            'rg_gb_a', 
            'rg_an_a', 
            'te_main', 
            'te_deriv', 
            'te_div', 
            'val_pec', 
            'sai_can', 
            'valv_ret_leve', 
            'valv_ret_pesado',
            'outro'])
        user_input_layout.addWidget(self.component_list,1,1)

        # Quantity
        self.quantity = QDoubleSpinBox()
        self.quantity.setValue(1)
        self.quantity.setMinimum(0)
        self.quantity.setDecimals(0)
        user_input_layout.addWidget(self.quantity,1,2)

        # Size
        self.c_size = QComboBox()
        self.c_size.addItems([
            "13 (1/2\")",
            "19 (3/4\")",
            "25 (1\")",
            "32 (1.1/4\")",
            "38 (1.1/2\")",
            "50 (2\")",
            "63 (2.1/2\")",
            "75 (3\")",
            "100 (4\")",
            "125 (5\")",
            "150 (6\")",
            "200 (8\")",
            "250 (10\")",
            "300 (12\")",
            "350 (14\")"
        ])
        user_input_layout.addWidget(self.c_size,1,3)

        # Path Flow
        self.flow = QDoubleSpinBox()
        self.flow.setMinimum(0)
        self.flow.setMaximum(100000)
        self.flow.setDecimals(2)
        self.flow.setSuffix("m³/h")
        user_input_layout.addWidget(self.flow,1,4)

        # Add Button
        add_button = QPushButton("Adicionar")
        add_button.clicked.connect(self.addConnection)
        user_input_layout.addWidget(add_button,1,5)
        top_widget = QWidget()
        top_widget.setLayout(user_input_layout)

        # Table
        self.table = QTableView()
        table_header = [["Trecho", "Conexão", "Quantidade/Comprimento", "Diâmetro", "Vazão", "Botãos"]]
        self.model = InputTable(table_header)  
        self.table.setModel(self.model)      

        # Bottom Widget
        calculate_button = QPushButton("Calcular")
        calculate_button.clicked.connect(self.calculate)

        # Main Widget
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(top_widget)
        vertical_layout.addWidget(self.table)
        vertical_layout.addWidget(calculate_button)
        

        main_widget = QWidget()
        main_widget.setLayout(vertical_layout)

        # Memory
        self.user_circuit = []

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(main_widget)


    def addConnection(self):
        current_index = self.path_index.value()
        current_quantity = self.quantity.value()
        current_component = self.component_list.currentText()
        current_size = self.c_size.currentText()
        current_flow = self.flow.value()
        self.user_circuit.append([current_index, current_component, current_size, current_quantity, current_flow])
        self.model._data.append((current_index, current_component, current_quantity, current_size, current_flow,"Botaos"))
        self.model.layoutChanged.emit()

    def calculate(self):
        eq_length = plotSystemPoint(self.user_circuit)
        None

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()