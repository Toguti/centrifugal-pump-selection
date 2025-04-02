from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QTabWidget,
    QMessageBox
)
from PyQt6.QtGui import QAction
import sys
from UI.fluid_prop_tab import FluidPropInput
from UI.pipe_table_tab import *
from UI.pump_selection_tab import PumpSelectionWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main window Layout
        self.setWindowTitle("Selecionador de Bombas")
        self.setMinimumSize(QSize(1200, 900))
  
        # Widgets
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_layout = QVBoxLayout(central_widget)

        # Tabs em Central Widget
        tab_widget = QTabWidget()

        # Criação das abas
        fluid_prop_tab = QWidget()
        system_input_tab = QWidget()
        pump_selection_tab = QWidget()

        # Adiciona abas ao QTabWidget
        tab_widget.addTab(fluid_prop_tab, "Propriedade do Fluido")
        tab_widget.addTab(system_input_tab, "Sistema")
        tab_widget.addTab(pump_selection_tab, "Seleção da Bomba")

        # Layouts para cada aba
        fluid_prop_tab_layout = QVBoxLayout(fluid_prop_tab)
        system_input_tab_layout = QVBoxLayout(system_input_tab)
        pump_selection_tab_layout = QVBoxLayout(pump_selection_tab)

        ## Configuração da aba "Propriedade do Fluido"
        self.fluid_prop_input_widget = FluidPropInput()
        fluid_prop_tab_layout.addWidget(self.fluid_prop_input_widget)

        ## Configuração da aba "Sistema"
        self.system_input_widget = SystemInputWidget()
        system_input_tab_layout.addWidget(self.system_input_widget)

        self.pump_selection_widget = PumpSelectionWidget(
            system_input_widget=self.system_input_widget,
            fluid_prop_input_widget=self.fluid_prop_input_widget
        )
        pump_selection_tab_layout.addWidget(self.pump_selection_widget)

        central_layout.addWidget(tab_widget)
        
        self.createMenuBar()

    def createMenuBar(self):
        menu_bar = self.menuBar()

        # Menu File
        file_menu = menu_bar.addMenu("File")
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(exit_action)

        # Menu Options
        options_menu = menu_bar.addMenu("Options")
        settings_action = QAction("Settings", self)
        options_menu.addAction(settings_action)

        # Menu About
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
