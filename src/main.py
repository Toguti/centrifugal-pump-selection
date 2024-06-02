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
    QLineEdit,
    QTableWidget,
    QTabWidget
)
import sys
from pressure_drop.local_loss import *
from pressure_drop.total_head_loss import *
from UI.system_calc import InputTable
from UI.fluid_system_input import fluid_system_input

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main window Layout
        self.setWindowTitle("Seletor de Bombas")
        self.setMinimumSize(QSize(1024, 768))
  
        # Widgets
        # Center
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        #Layout for the central widget
        central_layout = QVBoxLayout(central_widget)

        # Tabs in Central Widget
        tab_widget = QTabWidget()

        # Create Tabs 
        fluid_prop_tab = QWidget()
        system_input_tab = QWidget()
        pump_selection_tab = QWidget()

        # Add tabs to QTabWidget
        tab_widget.addTab(fluid_prop_tab, "Propriedade do Fluido")
        tab_widget.addTab(system_input_tab, "Sistema")
        tab_widget.addTab(pump_selection_tab, "Seleção da Bomba")

        # Set tabs Layouts
        fluid_prop_tab_layout = QVBoxLayout(fluid_prop_tab)
        system_input_tab_layout = QVBoxLayout(system_input_tab)
        pump_selection_tab_layout = QVBoxLayout(pump_selection_tab)

        ## Fluid properties tab configuration ##
        

        ## Sytem input tab configuration ##
        
        
        ## Pump seleciton tab configuration ##

        # # Bottom Widget
        # calculate_button = QPushButton("Calcular")
        # # calculate_button.clicked.connect(self.calculate)

        # # System Input
        # system_input = fluid_system_input()

        # # Input Section
        # input = fluid_system_input()

        # # Main Widget
        # vertical_layout = QVBoxLayout()

        # vertical_layout.addWidget(input)
        # # vertical_layout.addWidget(top_widget)
        # vertical_layout.addWidget(self.table)
        # vertical_layout.addWidget(calculate_button)
        

        # main_widget = QWidget()
        # main_widget.setLayout(vertical_layout)

        # Memory
        self.user_circuit = [] 

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        central_layout.addWidget(tab_widget)
        
    def calculate(self, max_flow=10, T_user=25, P_user=101325,fluid='INCOMP::Water'):
        fluid_properties = fluidProp(T_user, P_user, fluid)
        max_flow = 10
        plotCurve(self.user_circuit, max_flow, fluid_properties)

        None

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()