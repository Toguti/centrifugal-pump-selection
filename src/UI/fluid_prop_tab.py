# Adicione esta importação ao topo do arquivo
from PyQt6.QtWidgets import (
    QRadioButton, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, 
    QDoubleSpinBox, QButtonGroup, QApplication, QFormLayout, QGroupBox
)
from PyQt6.QtCore import Qt
from pyfluids import Fluid, FluidsList

class FluidPropInput(QWidget):
    def __init__(self):
        super().__init__()
        
        # Grupo de Fluido
        self.fluid_group = QGroupBox("Fluido")
        
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
        
        # Layout para o grupo de fluido
        self.fluid_inner_layout = QVBoxLayout()
        self.fluid_inner_layout.addLayout(self.radio_layout)
        self.fluid_inner_layout.addLayout(self.fluid_layout)
        self.fluid_inner_layout.addLayout(self.form_layout)
        self.fluid_group.setLayout(self.fluid_inner_layout)
        
        # Grupo de Tubulação
        self.tubing_group = QGroupBox("Tubulação")
        
        # Criar controles para tubulação
        self.norm_label = QLabel("Norma:")
        self.norm_combo = QComboBox()
        self.norm_combo.addItems(["ASME B36.10", "DIN 2448/1629", "NBR 5580", "JIS G3452"])
        
        self.material_label = QLabel("Material:")
        self.material_combo = QComboBox()
        self.material_combo.addItems(["Aço Carbono", "Aço Inox", "Aço Inox Polido"])
        
        self.roughness_label = QLabel("Rugosidade Interna:")
        self.roughness_input = QDoubleSpinBox()
        self.roughness_input.setRange(0, 10)
        self.roughness_input.setDecimals(3)
        self.roughness_input.setSuffix(" mm")
        self.roughness_input.setValue(0.045)  # Valor padrão para tubos de aço


        # Definir lista de materiais e rugosidades correspondentes
        self.materials = {
            "Aço comercial novo": 0.045,
            "Aço laminado novo": 0.05,
            "Ferro fundido novo": 0.25,
            "Ferro fundido oxidado": 1.0,
            "PVC": 0.0015,
            "Cobre": 0.0015,
            "Plásticos (genéricos)": 0.0025,
            "PEAD": 0.007
        }

        # Radio buttons para rugosidade
        self.roughness_radio1 = QRadioButton("Rugosidade Padrão")
        self.roughness_radio2 = QRadioButton("Rugosidade Personalizada")

        # Grupo de botões para rugosidade
        self.roughness_radio_group = QButtonGroup(self)
        self.roughness_radio_group.addButton(self.roughness_radio1)
        self.roughness_radio_group.addButton(self.roughness_radio2)
        self.roughness_radio_group.setExclusive(True)
        self.roughness_radio1.setChecked(True)

        # Connect radio buttons para habilitar/desabilitar entrada de rugosidade
        self.roughness_radio1.toggled.connect(self.toggle_roughness_input)
        self.roughness_radio2.toggled.connect(self.toggle_roughness_input)

        # Atualizar combobox de material
        self.material_combo.clear()
        self.material_combo.addItems(list(self.materials.keys()))
        self.material_combo.currentIndexChanged.connect(self.update_roughness)

        # Configurar spinbox de rugosidade
        self.roughness_input.setDisabled(True)
        

        # Layout para tubulação
        self.tubing_form_layout = QFormLayout()
        self.tubing_form_layout.addRow(self.norm_label, self.norm_combo)
        self.tubing_form_layout.addRow(self.material_label, self.material_combo)

        # Layout para opções de rugosidade
        self.roughness_radio_layout = QHBoxLayout()
        self.roughness_radio_layout.addWidget(self.roughness_radio1)
        self.roughness_radio_layout.addWidget(self.roughness_radio2)
        self.tubing_form_layout.addRow(QLabel("Modo:"), self.roughness_radio_layout)
        self.tubing_form_layout.addRow(self.roughness_label, self.roughness_input)

        self.tubing_group.setLayout(self.tubing_form_layout)
        
        # Layout principal
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.fluid_group)
        self.main_layout.addWidget(self.tubing_group)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.setSpacing(15)
        
        # Set the layout for the widget
        self.setLayout(self.main_layout)
        
        # Set window title and initial size
        self.setWindowTitle("Fluid Properties Input")
        self.resize(450, 400)
        
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

    def toggle_roughness_input(self):
        """Habilita/desabilita entrada de rugosidade personalizada."""
        if self.roughness_radio1.isChecked():
            self.roughness_input.setDisabled(True)
            self.update_roughness()
        else:
            self.roughness_input.setDisabled(False)

    def update_roughness(self):
        """Atualiza o valor de rugosidade com base no material selecionado."""
        if self.roughness_radio1.isChecked():
            material = self.material_combo.currentText()
            rugosidade = self.materials.get(material, 0.045)  # Valor padrão se não encontrado
            self.roughness_input.setValue(rugosidade)

    def get_mu_input_value(self):
        return self.mu_input.value()
        
    def get_rho_input_value(self):
        return self.rho_input.value()
    
    def get_roughness_value(self):
        return self.roughness_input.value()
        
    def get_material(self):
        return self.material_combo.currentText()
        
    def get_norm(self):
        return self.norm_combo.currentText()