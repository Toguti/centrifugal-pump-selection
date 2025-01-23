import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QFileDialog, QWidget, QMessageBox
from PyQt6.QtCharts import QChart, QChartView, QLineSeries
from PyQt6.QtGui import QPainter
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

class PumpSelectionApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pump Selection Application")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.label = QLabel("Select the system curve to find the best pump match:")
        self.layout.addWidget(self.label)

        self.select_button = QPushButton("Load System Curve")
        self.select_button.clicked.connect(self.load_system_curve)
        self.layout.addWidget(self.select_button)

        self.chart_view = QChartView()
        self.layout.addWidget(self.chart_view)

    def load_system_curve(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open System Curve File", "", "CSV Files (*.csv);;All Files (*)")

        if file_path:
            try:
                system_curve_data = np.loadtxt(file_path, delimiter=",", skiprows=1)
                system_flow, system_head = system_curve_data[:, 0], system_curve_data[:, 1]
                self.find_best_pump(system_flow, system_head)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load system curve: {e}")

    def find_best_pump(self, system_flow, system_head):
        conn = sqlite3.connect("pumps.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, flow, head FROM pumps")
        pumps = cursor.fetchall()

        best_pump = None
        best_error = float('inf')

        for pump in pumps:
            pump_id, pump_flow, pump_head = pump
            pump_flow = np.array(list(map(float, pump_flow.split(','))))
            pump_head = np.array(list(map(float, pump_head.split(','))))

            if len(pump_flow) != len(system_flow):
                continue

            error = np.sum((np.interp(system_flow, pump_flow, pump_head) - system_head) ** 2)

            if error < best_error:
                best_error = error
                best_pump = pump

        conn.close()

        if best_pump:
            self.display_pump_curve(best_pump, system_flow, system_head)
        else:
            QMessageBox.warning(self, "No Match", "No suitable pump found for the given system curve.")

    def display_pump_curve(self, pump, system_flow, system_head):
        pump_id, pump_flow, pump_head = pump
        pump_flow = np.array(list(map(float, pump_flow.split(','))))
        pump_head = np.array(list(map(float, pump_head.split(','))))

        chart = QChart()
        chart.setTitle(f"Best Pump Match (Pump ID: {pump_id})")

        system_curve = QLineSeries()
        system_curve.setName("System Curve")
        for x, y in zip(system_flow, system_head):
            system_curve.append(x, y)
        chart.addSeries(system_curve)

        pump_curve = QLineSeries()
        pump_curve.setName("Pump Curve")
        for x, y in zip(pump_flow, pump_head):
            pump_curve.append(x, y)
        chart.addSeries(pump_curve)

        chart.createDefaultAxes()
        self.chart_view.setChart(chart)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PumpSelectionApp()
    window.show()

    sys.exit(app.exec())
