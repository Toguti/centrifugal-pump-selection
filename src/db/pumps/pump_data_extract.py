import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from matplotlib.backends.backend_pdf import PdfPages

# Constantes
HEADER_DATA_ROW = 2  # índice a partir do qual os dados numéricos começam
POLY_DEGREE = 5      # grau do polinômio para ajuste

def parse_pump_data(file_path):
    """
    Lê o arquivo CSV e organiza os dados em um dicionário estruturado.
    
    Cada par de colunas (X e Y) é identificado por um cabeçalho no formato 'diameter_curveType'
    e os dados são extraídos a partir da linha HEADER_DATA_ROW.
    
    Parâmetros:
        file_path (str): caminho para o arquivo CSV.
    
    Retorna:
        dict: Dicionário contendo os dados organizados por diâmetro e tipo de curva.
    """
    try:
        df = pd.read_csv(file_path, header=None)
    except Exception as e:
        print(f"Erro ao ler o arquivo {file_path}: {e}")
        return {}
    
    pump_data = {}
    num_cols = df.shape[1]
    col_idx = 0
    
    while col_idx < num_cols:
        header = str(df.iloc[0, col_idx])
        if pd.isna(header):
            col_idx += 1
            continue
        
        header_parts = header.split('_')
        # Verifica se o cabeçalho segue o padrão esperado: "diameter_curveType"
        if len(header_parts) != 2:
            col_idx += 1
            continue
        
        diameter, curve_type = header_parts[0], header_parts[1]
        if col_idx + 1 >= num_cols:
            break
        
        # Extração dos dados a partir da linha definida por HEADER_DATA_ROW
        try:
            x_values = df.iloc[HEADER_DATA_ROW:, col_idx].dropna().astype(float).tolist()
            y_values = df.iloc[HEADER_DATA_ROW:, col_idx + 1].dropna().astype(float).tolist()
        except Exception as e:
            print(f"Erro ao processar dados na coluna {col_idx} do arquivo {file_path}: {e}")
            col_idx += 2
            continue
        
        if diameter not in pump_data:
            pump_data[diameter] = {}
        
        pump_data[diameter][curve_type] = {'X': x_values, 'Y': y_values}
        col_idx += 2
    
    return pump_data


def fit_polynomial(pump_data, degree=POLY_DEGREE):
    """
    Ajusta um polinômio aos dados de cada curva e retorna os coeficientes.
    
    Se houver a chave 'all', aplica o ajuste aos demais diâmetros.
    
    Parâmetros:
        pump_data (dict): Dicionário com os dados extraídos.
        degree (int): Grau do polinômio para o ajuste.
    
    Retorna:
        dict: Dicionário com os coeficientes ajustados organizados por diâmetro e tipo de curva.
    """
    poly_fits = {}
    
    # Processamento especial para a chave "all"
    if 'all' in pump_data:
        all_data = pump_data['all']
        available_diameters = [diameter for diameter in pump_data.keys() if diameter != 'all']
        
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
    
    # Processamento para os demais diâmetros
    for diameter, curves in pump_data.items():
        if diameter == 'all':
            continue
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


def plot_all_curves(pump_data, poly_fits):
    """
    Plota e exibe os gráficos das curvas originais e dos ajustes polinomiais.
    
    Parâmetros:
        pump_data (dict): Dicionário com os dados extraídos.
        poly_fits (dict): Dicionário com os coeficientes polinomiais.
    """
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
    """
    Salva os gráficos gerados para cada curva em um arquivo PDF.
    
    Parâmetros:
        pump_data_list (list): Lista de dicionários com os dados extraídos de cada arquivo.
        poly_fits_list (list): Lista de dicionários com os coeficientes ajustados de cada arquivo.
        output_pdf (str): Caminho do arquivo PDF de saída.
    """
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


def process_file(file_name, raw_data_path, output_path, degree=POLY_DEGREE):
    """
    Processa um único arquivo:
      - Extrai os dados e ajusta os polinômios.
      - Calcula o intervalo de fluxo (mínimo e máximo) usando a curva "headxflow".
      - Extrai os metadados do nome do arquivo (Marca, Modelo e Rotation).
      - Agrupa os coeficientes das 4 curvas em uma única linha, criando as colunas:
        "flowxhead", "flowxeff", "flowxnpsh" e "flowxpower".
      - Exporta as informações em um arquivo CSV.
    
    Parâmetros:
        file_name (str): Nome do arquivo a ser processado.
        raw_data_path (str): Caminho para o diretório de arquivos de entrada.
        output_path (str): Caminho para o diretório de saída.
        degree (int): Grau do polinômio para ajuste.
    """
    file_path = os.path.join(raw_data_path, file_name)
    output_file = os.path.join(output_path, file_name.replace(".csv", "_polycoeff.csv"))
    
    # Processamento dos dados do arquivo
    pump_data = parse_pump_data(file_path)
    if not pump_data:
        print(f"Arquivo {file_name} não foi processado devido a erros na leitura dos dados.")
        return None, None
    
    poly_fits = fit_polynomial(pump_data, degree=degree)
    
    # Extrair os metadados do nome do arquivo com tratamento de erro
    file_base = os.path.splitext(file_name)[0]
    parts = file_base.split("_")
    try:
        marca = parts[0]
        modelo = parts[1] if len(parts) > 1 else ""
        rotation = parts[3] if len(parts) > 3 else ""
    except Exception as e:
        print(f"Erro ao extrair metadados do arquivo {file_name}: {e}")
        marca, modelo, rotation = "", "", ""
    
    # Calcula os valores mínimo e máximo de fluxo (flow) para cada diâmetro, usando a curva "headxflow"
    flow_range = {}
    for diameter, curves in pump_data.items():
        if diameter == "all":
            continue
        if "headxflow" in curves:
            x_values = curves["headxflow"]['X']
            flow_range[diameter] = (min(x_values), max(x_values))
        else:
            flow_range[diameter] = (None, None)
    
    # Agrupar os coeficientes para cada diâmetro em uma única linha,
    # distribuindo-os nas colunas "flowxhead", "flowxeff", "flowxnpsh" e "flowxpower".
    rows = []
    for diameter, curves_poly in poly_fits.items():
        min_flow, max_flow = flow_range.get(diameter, (None, None))
        # Obter os coeficientes para cada curva, usando string vazia caso não existam
        flowxhead = curves_poly.get("headxflow", "")
        flowxeff  = curves_poly.get("effxflow", "")
        flowxnpsh = curves_poly.get("npshxflow", "")
        flowxpower = curves_poly.get("powerxflow", "")
        # Nova ordem: Marca, Modelo, Diameter, Rotation, min_flow, max_flow, flowxhead, flowxeff, flowxnpsh, flowxpower
        row = (marca, modelo, diameter, rotation, min_flow, max_flow, flowxhead, flowxeff, flowxnpsh, flowxpower)
        rows.append(row)
    
    # Definindo o cabeçalho desejado com as colunas na nova ordem
    columns = ["Marca", "Modelo", "Diameter", "Rotation", "min_flow", "max_flow",
               "flowxhead", "flowxeff", "flowxnpsh", "flowxpower"]
    
    poly_df = pd.DataFrame(rows, columns=columns)
    
    try:
        poly_df.to_csv(output_file, index=False)
        print(f"Coeficientes polinomiais salvos em: {output_file}")
    except Exception as e:
        print(f"Erro ao salvar CSV {output_file}: {e}")
    
    return pump_data, poly_fits


if __name__ == "__main__":
    raw_data_path = "src/db/pumps/raw_data"
    output_path = "src/db/pumps/processed_data"
    output_pdf = os.path.join(output_path, "all_pump_curves.pdf")
    
    # Lista para armazenar os dados de cada arquivo para posterior geração de PDF
    pump_data_list = []
    poly_fits_list = []
    
    # Processa cada arquivo no diretório de entrada
    for file_name in os.listdir(raw_data_path):
        print(f"Processando arquivo: {file_name}")
        pump_data, poly_fits = process_file(file_name, raw_data_path, output_path, degree=POLY_DEGREE)
        if pump_data is not None and poly_fits is not None:
            pump_data_list.append(pump_data)
            poly_fits_list.append(poly_fits)
    
    # Gera um PDF com os gráficos de todas as curvas processadas
    save_plots_to_pdf(pump_data_list, poly_fits_list, output_pdf)
