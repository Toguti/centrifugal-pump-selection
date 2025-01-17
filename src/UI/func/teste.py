from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QSpinBox, QVBoxLayout, QHBoxLayout, QPushButton
import sys

class DynamicWidgets(QWidget):
    def __init__(self):
        super().__init__()
        self.spin_boxes = []  # List to store QSpinBox references
        self.init_ui()

    def init_ui(self):
        # Arrays for labels and spinbox default values
        labels = ["Item 1", "Item 2", "Item 3", "Item 4"]
        spin_defaults = [0, 5, 10, 15]

        # Main vertical layout
        main_layout = QVBoxLayout()

        # Loop to create QLabel and QSpinBox pairs
        for text, default_value in zip(labels, spin_defaults):
            # Horizontal layout for each pair
            h_layout = QHBoxLayout()

            # Create QLabel
            label = QLabel(text)
            
            # Create QSpinBox
            spin_box = QSpinBox()
            spin_box.setValue(default_value)
            spin_box.setRange(0, 100)  # Optional: set the range

            # Store the spin box reference
            self.spin_boxes.append(spin_box)

            # Add label and spin box to horizontal layout
            h_layout.addWidget(label)
            h_layout.addWidget(spin_box)

            # Add horizontal layout to the main layout
            main_layout.addLayout(h_layout)

        # Add a button to trigger value collection
        get_values_button = QPushButton("Get SpinBox Values")
        get_values_button.clicked.connect(self.get_spinbox_values)
        main_layout.addWidget(get_values_button)

        self.setLayout(main_layout)
        self.setWindowTitle("Dynamic QLabel and QSpinBox Example")
        self.show()

    def get_spinbox_values(self):
        # Collect values from all QSpinBox widgets
        values = [spin_box.value() for spin_box in self.spin_boxes]
        print("SpinBox Values:", values)  # Print or process the values

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DynamicWidgets()
    sys.exit(app.exec())
