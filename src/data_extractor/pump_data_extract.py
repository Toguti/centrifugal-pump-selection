import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from matplotlib.backends.backend_pdf import PdfPages

def parse_pump_data(file_path):
    df = pd.read_csv(file_path, header=None)
    pump_data = {}
    num_cols = df.shape[1]
    col_idx = 0
    
    while col_idx < num_cols:
        header = str(df.iloc[0, col_idx])
        if pd.isna(header):
            col_idx += 1
            continue
        
        parts = header.split('_')
        if len(parts) != 2:
            col_idx += 1
            continue
        
        diametro, tipo_grafico = parts[0], parts[1]
        if col_idx + 1 >= num_cols:
            break
        
        eixo_x = df.iloc[2:, col_idx].dropna().astype(float).tolist()
        eixo_y = df.iloc[2:, col_idx + 1].dropna().astype(float).tolist()
        
        if diametro not in pump_data:
            pump_data[diametro] = {}
        
        pump_data[diametro][tipo_grafico] = {'X': eixo_x, 'Y': eixo_y}
        col_idx += 2
    
    return pump_data


def fit_polynomial(pump_data, degree=3):
    poly_fits = {}
    
    if 'all' in pump_data:
        all_data = pump_data['all']
        available_diameters = [d for d in pump_data.keys() if d != 'all']
        
        for curve_type, data in all_data.items():
            x = np.array(data['X'])
            y = np.array(data['Y'])
            
            if len(x) < degree + 1:
                continue  # Evita erro de ajuste para poucos pontos
            
            coeffs = np.polyfit(x, y, degree)
            
            for diameter in available_diameters:
                if diameter not in poly_fits:
                    poly_fits[diameter] = {}
                poly_fits[diameter][curve_type] = json.dumps(coeffs.tolist())
    
    for diameter, curves in pump_data.items():
        if diameter == 'all':
            continue  # Já processado
        
        if diameter not in poly_fits:
            poly_fits[diameter] = {}
        
        for curve_type, data in curves.items():
            x = np.array(data['X'])
            y = np.array(data['Y'])
            
            if len(x) < degree + 1:
                continue  # Evita erro de ajuste para poucos pontos
            
            coeffs = np.polyfit(x, y, degree)
            poly_fits[diameter][curve_type] = json.dumps(coeffs.tolist())
    
    return poly_fits


def get_pump_curve(diameter, curve_type, pump_data):
    if diameter in pump_data and curve_type in pump_data[diameter]:
        return pump_data[diameter][curve_type]
    return None


def plot_all_curves(pump_data, poly_fits):
    for diameter, curves in pump_data.items():
        for curve_type, data in curves.items():
            x = np.array(data['X'])
            y = np.array(data['Y'])
            
            plt.figure(figsize=(8, 5))
            plt.scatter(x, y, label='Dados originais', color='blue')
            
            if diameter in poly_fits and curve_type in poly_fits[diameter]:
                coeffs = json.loads(poly_fits[diameter][curve_type])
                x_fit = np.linspace(min(x), max(x), 100)
                y_fit = np.polyval(coeffs, x_fit)
                plt.plot(x_fit, y_fit, label='Ajuste Polinomial', color='red')
            
            plt.xlabel('Fluxo (m³/h)')
            plt.ylabel('Valor')
            plt.title(f'Curva {curve_type} para Rotor {diameter} mm')
            plt.legend()
            plt.grid()
            plt.show()

def save_plots_to_pdf(pump_data_list, poly_fits_list, output_pdf):
    with PdfPages(output_pdf) as pdf:
        for pump_data, poly_fits in zip(pump_data_list, poly_fits_list):
            for diameter, curves in pump_data.items():
                for curve_type, data in curves.items():
                    x = np.array(data['X'])
                    y = np.array(data['Y'])
                    
                    plt.figure(figsize=(8, 5))
                    plt.scatter(x, y, label='Dados originais', color='blue')
                    
                    if diameter in poly_fits and curve_type in poly_fits[diameter]:
                        coeffs = json.loads(poly_fits[diameter][curve_type])
                        x_fit = np.linspace(min(x), max(x), 100)
                        y_fit = np.polyval(coeffs, x_fit)
                        plt.plot(x_fit, y_fit, label='Ajuste Polinomial', color='red')
                    
                    plt.xlabel('Fluxo (m³/h)')
                    plt.ylabel('Valor')
                    plt.title(f'Curva {curve_type} para Rotor {diameter} mm')
                    plt.legend()
                    plt.grid()
                    pdf.savefig()
                    plt.close()
    
    print(f"Gráficos salvos em {output_pdf}")

if __name__ == "__main__":
    raw_data_path = "src/db/pumps/raw_data"
    output_path = "src/db/pumps/processed_data"
    output_pdf = os.path.join(output_path, "all_pump_curves.pdf")
    
    pump_data_list = []
    poly_fits_list = []
    
    for file in os.listdir(raw_data_path):
        print(file)
        file_path = os.path.join(raw_data_path, file)
        output_file = os.path.join(output_path, file.replace(".csv", "_polycoeff.csv"))
    
        pump_data = parse_pump_data(file_path)
        poly_fits = fit_polynomial(pump_data, degree=5)
        
        pump_data_list.append(pump_data)
        poly_fits_list.append(poly_fits)
    
        # Salvar coeficientes polinomiais em um CSV
        poly_df = pd.DataFrame([(d, c, poly_fits[d][c]) for d in poly_fits for c in poly_fits[d]], 
                                columns=["Diameter", "Curve Type", "Coefficients"])
        poly_df.to_csv(output_file, index=False)
        print(f"Coeficientes polinomiais salvos em: {output_file}")
    
    # Salvar gráficos de todos os arquivos em um único PDF
    save_plots_to_pdf(pump_data_list, poly_fits_list, output_pdf)