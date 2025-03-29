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
    
    Cada par de colunas (X e Y) é identificado por um cabeçalho no formato 'diameter_stages_curveType'
    e os dados são extraídos a partir da linha HEADER_DATA_ROW.
    
    Parâmetros:
        file_path (str): caminho para o arquivo CSV.
    
    Retorna:
        dict: Dicionário contendo os dados organizados por diâmetro, estágios e tipo de curva.
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
        # Verifica se o cabeçalho segue o padrão esperado: "diameter_stages_curveType"
        if len(header_parts) != 3:
            col_idx += 1
            continue
        
        diameter, stages, curve_type = header_parts[0], header_parts[1], header_parts[2]
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
        
        diameter_key = f"{diameter}_{stages}"
        if diameter_key not in pump_data:
            pump_data[diameter_key] = {}
        
        pump_data[diameter_key][curve_type] = {'X': x_values, 'Y': y_values}
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
        dict: Dicionário com os coeficientes ajustados organizados por diâmetro_estágios e tipo de curva.
    """
    poly_fits = {}
    
    # Processamento especial para a chave "all"
    all_key = next((k for k in pump_data.keys() if k.startswith('all_')), None)
    if all_key:
        all_data = pump_data[all_key]
        available_diameters = [diameter for diameter in pump_data.keys() if not diameter.startswith('all_')]
        
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
    for diameter_key, curves in pump_data.items():
        if diameter_key.startswith('all_'):
            continue
        if diameter_key not in poly_fits:
            poly_fits[diameter_key] = {}
        for curve_type, data in curves.items():
            x = np.array(data['X'])
            y = np.array(data['Y'])
            if len(x) < degree + 1:
                continue  # Evita erro de ajuste para poucos pontos
            coeffs = np.polyfit(x, y, degree)
            poly_fits[diameter_key][curve_type] = json.dumps(coeffs.tolist())
    
    return poly_fits

def plot_all_curves(pump_data, poly_fits):
    """
    Plota e exibe os gráficos das curvas originais e dos ajustes polinomiais.
    
    Parâmetros:
        pump_data (dict): Dicionário com os dados extraídos.
        poly_fits (dict): Dicionário com os coeficientes polinomiais.
    """
    for diameter_key, curves in pump_data.items():
        diameter_parts = diameter_key.split('_')
        diameter = diameter_parts[0]
        stages = diameter_parts[1] if len(diameter_parts) > 1 else "1"  # Estágio padrão 1 se não especificado
        
        for curve_type, data in curves.items():
            x = np.array(data['X'])
            y = np.array(data['Y'])
            
            plt.figure(figsize=(8, 5))
            plt.scatter(x, y, label='Dados originais', color='blue')
            
            if diameter_key in poly_fits and curve_type in poly_fits[diameter_key]:
                coeffs = json.loads(poly_fits[diameter_key][curve_type])
                x_fit = np.linspace(min(x), max(x), 100)
                y_fit = np.polyval(coeffs, x_fit)
                plt.plot(x_fit, y_fit, label='Ajuste Polinomial', color='red')
            
            plt.xlabel('Fluxo (m³/h)')
            plt.ylabel('Valor')
            plt.title(f'Curva {curve_type} para Rotor {diameter} mm e {stages} estágio(s)')
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
            for diameter_key, curves in pump_data.items():
                diameter_parts = diameter_key.split('_')
                diameter = diameter_parts[0]
                stages = diameter_parts[1] if len(diameter_parts) > 1 else "1"
                
                for curve_type, data in curves.items():
                    x = np.array(data['X'])
                    y = np.array(data['Y'])
                    
                    plt.figure(figsize=(8, 5))
                    plt.scatter(x, y, label='Dados originais', color='blue')
                    
                    if diameter_key in poly_fits and curve_type in poly_fits[diameter_key]:
                        coeffs = json.loads(poly_fits[diameter_key][curve_type])
                        x_fit = np.linspace(min(x), max(x), 100)
                        y_fit = np.polyval(coeffs, x_fit)
                        plt.plot(x_fit, y_fit, label='Ajuste Polinomial', color='red')
                    
                    plt.xlabel('Fluxo (m³/h)')
                    plt.ylabel('Valor')
                    plt.title(f'Curva {curve_type} para Rotor {diameter} mm e {stages} estágio(s)')
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
      - Extrai os metadados do nome do arquivo (Marca, Modelo, Rotation).
      - Agrupa os coeficientes das 4 curvas em uma única linha, criando as colunas:
        "flowxhead", "flowxeff", "flowxnpsh" e "flowxpower".
      - A partir da curva "effxflow", calcula:
          * eff_bop: máxima eficiência.
          * eff_bop_flow: fluxo correspondente a eff_bop.
          * 80_eff_bop_flow = 0.8 * eff_bop_flow, limitado pelo min_flow.
          * 110_eff_bop_flow = 1.1 * eff_bop_flow, limitado pelo max_flow.
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
    
    # Calcula os valores mínimo e máximo de fluxo (flow) para cada combinação de diâmetro e estágios
    flow_range = {}
    for diameter_key, curves in pump_data.items():
        if diameter_key.startswith("all"):
            continue
        if "headxflow" in curves:
            x_values = curves["headxflow"]['X']
            flow_range[diameter_key] = (min(x_values), max(x_values))
        else:
            flow_range[diameter_key] = (None, None)
    
    # Para cada combinação de diâmetro e estágios, calcular os novos parâmetros a partir da curva "effxflow"
    additional_data = {}
    for diameter_key, curves in pump_data.items():
        if diameter_key.startswith("all"):
            continue
        eff_bop = ""
        eff_bop_flow = ""
        eff80_flow = ""
        eff110_flow = ""
        
        if "effxflow" in curves:
            x_eff = np.array(curves["effxflow"]['X'])
            y_eff = np.array(curves["effxflow"]['Y'])
            # Filtrar pontos dentro do intervalo [min_flow, max_flow]
            min_flow, max_flow = flow_range.get(diameter_key, (None, None))
            if min_flow is not None and max_flow is not None:
                mask = (x_eff >= min_flow) & (x_eff <= max_flow)
                if np.any(mask):
                    x_filtered = x_eff[mask]
                    y_filtered = y_eff[mask]
                else:
                    x_filtered = x_eff
                    y_filtered = y_eff
            else:
                x_filtered = x_eff
                y_filtered = y_eff
            if len(y_filtered) > 0:
                idx_max = np.argmax(y_filtered)
                eff_bop = y_filtered[idx_max]
                eff_bop_flow = x_filtered[idx_max]
                # Calcula os novos fluxos em relação a eff_bop_flow
                target80 = 0.8 * eff_bop_flow
                target110 = 1.1 * eff_bop_flow
                # Limita target80 ao mínimo e target110 ao máximo
                eff80_flow = target80 if target80 >= min_flow else min_flow
                eff110_flow = target110 if target110 <= max_flow else max_flow
        additional_data[diameter_key] = (eff_bop, eff_bop_flow, eff80_flow, eff110_flow)
    
    # Agrupar os coeficientes para cada diâmetro e estágio em uma única linha
    rows = []
    for diameter_key, curves_poly in poly_fits.items():
        # Extrair diâmetro e estágios da chave composta
        diameter_parts = diameter_key.split('_')
        diameter = diameter_parts[0]
        stages = diameter_parts[1] if len(diameter_parts) > 1 else "1"
        
        min_flow, max_flow = flow_range.get(diameter_key, (None, None))
        # Obter os coeficientes para cada curva, usando string vazia caso não existam
        flowxhead = curves_poly.get("headxflow", "")
        flowxeff = curves_poly.get("effxflow", "")
        flowxnpsh = curves_poly.get("npshxflow", "")
        flowxpower = curves_poly.get("powerxflow", "")
        # Obter os novos parâmetros calculados para a curva effxflow
        eff_bop, eff_bop_flow, eff80_flow, eff110_flow = additional_data.get(diameter_key, ("", "", "", ""))
        # Nova ordem: Marca, Modelo, Diameter, Rotation, Stages, min_flow, max_flow,
        # flowxhead, flowxeff, flowxnpsh, flowxpower, eff_bop, eff_bop_flow, 80_eff_bop_flow, 110_eff_bop_flow
        row = (marca, modelo, diameter, rotation, stages, min_flow, max_flow, flowxhead, flowxeff, flowxnpsh, flowxpower,
               eff_bop, eff_bop_flow, eff80_flow, eff110_flow)
        rows.append(row)
    
    # Definindo o cabeçalho desejado com as colunas na nova ordem
    columns = ["Marca", "Modelo", "Diameter", "Rotation", "Stages", "min_flow", "max_flow",
               "flowxhead", "flowxeff", "flowxnpsh", "flowxpower",
               "eff_bop", "eff_bop_flow", "p80_eff_bop_flow", "p110_eff_bop_flow"]
    
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
    # output_pdf = os.path.join(output_path, "all_pump_curves.pdf")
    
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
    # save_plots_to_pdf(pump_data_list, poly_fits_list, output_pdf)