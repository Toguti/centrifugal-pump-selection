from PyQt6.QtCore import Qt
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
    QGridLayout
)
import sys
from pressure_drop.local_loss import *



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Variables
        self.counter = 1

        # Main window Layout
        self.setWindowTitle("Pressure Loss Calculator")

        # User input widget
        user_input_layout = QGridLayout()


        user_input_layout.addWidget(QLabel("Index"),0,0)
        user_input_layout.addWidget(QLabel("Conexão"),0,1)
        user_input_layout.addWidget(QLabel("Diâmetro"),0,2)
        user_input_layout.addWidget(QLabel("Quantidade"),0,3)

        
        user_input_layout.addWidget(QLabel(str(self.counter)),1,0)
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
        self.size = QComboBox()
        self.size.addItems([
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
            "350 (14\")",
        ])
        user_input_layout.addWidget(self.size,1,3)

        # Add Button
        add_button = QPushButton("Adicionar")
        add_button.clicked.connect(self.addConnection)
        user_input_layout.addWidget(add_button,1,4)
        top_widget = QWidget()
        top_widget.setLayout(user_input_layout)

        # System Layout
        self.list_layout = QGridLayout()
        self.list_layout.addWidget(QLabel("Index"),0,0)
        self.list_layout.addWidget(QLabel("Conexão"),0,1)
        self.list_layout.addWidget(QLabel("Quantidade"),0,2)
        self.list_layout.addWidget(QLabel("Diâmetro"),0,3)
        self.list_layout.addWidget(QLabel("Botaos"),0,4)
        list_widget = QWidget()
        list_widget.setLayout(self.list_layout)
        
        # buttons Widget
        calculate_button = QPushButton("Calcular")
        calculate_button.clicked.connect(self.calculate)

        button_layout = QHBoxLayout()
        button_layout.addWidget(calculate_button)
        
        bottom_widget = QWidget()
        bottom_widget.setLayout(button_layout)

        # Main Widget
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(top_widget)
        vertical_layout.addWidget(list_widget)
        vertical_layout.addWidget(bottom_widget)

        main_widget = QWidget()
        main_widget.setLayout(vertical_layout)

        # Memory
        self.user_circuit = []

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(main_widget)


    def addConnection(self):
        self.list_layout.addWidget(QLabel(str(self.counter)),self.counter,0)
        self.list_layout.addWidget(QLabel(self.component_list.currentText()),self.counter,1)
        self.list_layout.addWidget(QLabel(str(self.quantity.value())),self.counter,2)
        self.list_layout.addWidget(QLabel(str(self.size.currentText())),self.counter,3)
        self.list_layout.addWidget(QLabel("Botaos"),self.counter,4)
        self.user_circuit.append([self.counter,self.component_list.currentText(), self.size.currentText(),self.quantity.value()])
        self.counter += 1
        print(self.user_circuit)

    def calculate(self):
        eq_length = sum_equivalent_length(self.user_circuit)
        print(eq_length)
        
app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()