from PyQt6.QtWidgets import (
    QRadioButton, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, 
    QDoubleSpinBox, QButtonGroup, QApplication, QFormLayout
)
from PyQt6.QtCore import Qt
from pyfluids import Fluid, FluidsList

class FluidPropInput(QWidget):
    def __init__(self):
        super().__init__()
        
        # Create combo box for "Fluido:"
        self.fluid_label = QLabel("Fluido:")
        self.fluid_combo = QComboBox()
        self.fluid_combo.addItems(["Água"])  # Add your options here
        self.fluid_combo.currentIndexChanged.connect(self.change_values)
        
        # Create radio buttons
        self.radio1 = QRadioButton("Fluidos Padrões")
        self.radio2 = QRadioButton("Fluido Personalizado")

        # Ensure only one radio button can be selected at a time
        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.radio1)
        self.radio_group.addButton(self.radio2)
        self.radio_group.setExclusive(True)
        
        # Set radio1 to be checked at launch
        self.radio1.setChecked(True)

        # Connect radio buttons to a function to enable/disable inputs
        self.radio1.toggled.connect(self.toggle_inputs)
        self.radio2.toggled.connect(self.toggle_inputs)

        # Create labels and spin boxes for number input
        self.temperature_label = QLabel("Temperatura (°C):")
        self.temperature_input = QDoubleSpinBox()
        self.temperature_input.setRange(-100, 1000)
        self.temperature_input.setDecimals(1)
        self.temperature_input.setSuffix(" °C")
        self.temperature_input.setValue(25.0)
        
        self.mu_label = QLabel("µ (Viscosidade Absoluta [cP]):")
        self.mu_input = QDoubleSpinBox()
        self.mu_input.setRange(0.001, 2)
        self.mu_input.setDecimals(3)
        self.mu_input.setSuffix(" cP")
        self.mu_input.setValue(0.891)
        
        self.rho_label = QLabel("ρ (Massa Específica):")
        self.rho_input = QDoubleSpinBox()
        self.rho_input.setRange(0, 5000)
        self.rho_input.setDecimals(1)
        self.rho_input.setSuffix(" kg/m³")
        self.rho_input.setValue(1000)
        
        # Initially disable "µ (mu)" and "ρ (rho)" inputs
        self.mu_input.setDisabled(True)
        self.rho_input.setDisabled(True)

        # Layout for the fluid selection
        self.fluid_layout = QHBoxLayout()
        self.fluid_layout.addWidget(self.fluid_label)
        self.fluid_layout.addWidget(self.fluid_combo)
        
        # Layout for radio buttons
        self.radio_layout = QHBoxLayout()
        self.radio_layout.addWidget(self.radio1)
        self.radio_layout.addWidget(self.radio2)

        # Form layout for better alignment
        self.form_layout = QFormLayout()
        self.form_layout.addRow(self.temperature_label, self.temperature_input)
        self.form_layout.addRow(self.mu_label, self.mu_input)
        self.form_layout.addRow(self.rho_label, self.rho_input)
        
        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.radio_layout)
        self.main_layout.addLayout(self.fluid_layout)
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.setSpacing(10)
        
        # Set the layout for the widget
        self.setLayout(self.main_layout)
        
        # Set window title and initial size
        self.setWindowTitle("Fluid Properties Input")
        self.resize(400, 200)
        
    def toggle_inputs(self):
        if self.radio1.isChecked():
            self.mu_input.setDisabled(True)
            self.rho_input.setDisabled(True)
        elif self.radio2.isChecked():
            self.mu_input.setDisabled(False)
            self.rho_input.setDisabled(False)

    
    def change_values(self):
        try:
            self.mu_input.setValue(CP.PropsSI('V', 'T', self.temperature_input.value() + 273.15, 'P', 101325, self.fluid_combo.currentText())*1000)
        except ValueError:
            print("Erro!!!! Não foi encontrado um valor de Viscosidade Dinamica para", self.fluid_combo.currentText(), "Insira um valor Manualmente")
    
        try:    
            self.rho_input.setValue(CP.PropsSI('D', 'T', self.temperature_input.value() + 273.15, 'P', 101325, self.fluid_combo.currentText()))
        except ValueError:
            print("Erro!!!! Não foi encontrado um valor de Densidade para", self.fluid_combo.currentText(), "Insira um valor Manualmente")
    # (self.temperature_input.value() + 273.15)

    def get_mu_input_value(self):
        return self.mu_input.value()
    def get_rho_input_value(self):
        return self.rho_input.value()