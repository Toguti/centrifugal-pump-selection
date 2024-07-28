from PyQt6.QtCore import (QSize
                          )
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTabWidget,
    QMessageBox,
    QPushButton
)
from PyQt6.QtGui import (
    QAction
)
import sys
from UI.system_calc import InputTable
from UI.fluid_prop_tab import FluidPropInput
from UI.pipe_table_tab import PipeTableWidget
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main window Layout
        self.setWindowTitle("Seletor de Bombas")
        self.setMinimumSize(QSize(1200, 768))
  
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
        fluid_prop_input_widget = FluidPropInput()
        fluid_prop_tab_layout.addWidget(fluid_prop_input_widget)

        ## Sytem input tab configuration ##
        
        self.pipe_table_widget = PipeTableWidget(2, 26)
        system_input_tab_layout.addWidget(self.pipe_table_widget)


        # System Input Buttons

        add_row_button = QPushButton("Adicionar Linha")
        add_row_button.clicked.connect(self.pipe_table_widget.addRow)

        calculate_button = QPushButton("Calcular")
        calculate_button.clicked.connect(self.calculate)

        system_buttons_widget = QWidget()
        system_buttons_layout = QHBoxLayout(system_buttons_widget)
        system_buttons_layout.addWidget(add_row_button)
        system_buttons_layout.addWidget(calculate_button)
        system_input_tab_layout.addWidget(system_buttons_widget)


        
        # System Input Buttons
        
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
        
        ## Create the menu bar
        self.createMenuBar()


    def calculate(self, max_flow=10, T_user=25, P_user=101325,fluid='INCOMP::Water'):
        # fluid_properties = fluidProp(T_user, P_user, fluid)
        # max_flow = 10
        # plotCurve(self.user_circuit, max_flow, fluid_properties)
        print(self.pipe_table_widget.retriveData())
        None

    def createMenuBar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(exit_action)

        # Options menu
        options_menu = menu_bar.addMenu("Options")
        settings_action = QAction("Settings", self)
        options_menu.addAction(settings_action)

        # About menu
        about_menu = menu_bar.addMenu("About")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.showAboutDialog)
        about_menu.addAction(about_action)

    def showAboutDialog(self):
        QMessageBox.about(self, "About", "This is a PyQt6 application demonstrating a rotated table.")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())