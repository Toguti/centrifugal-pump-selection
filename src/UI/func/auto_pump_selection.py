#!/usr/bin/env python3
"""
Módulo: auto_pump_selection.py
Descrição:
    Seleciona modelos de bombas cujas curvas (coef_head) se interceptam com a curva do sistema
    no intervalo global definido por global_min_flow e global_max_flow. Apenas bombas que
    possuam valores de vazão (vazao_min e vazao_max) dentro deste intervalo serão consideradas.
    
Funcionalidades:
    - Recebe uma curva do sistema (coef_system_curve) que é um array de coeficientes polinomiais (grau 5).
    - Recebe as variáveis global_min_flow e global_max_flow que definem o intervalo global de fluxo.
    - Realiza uma consulta no banco de dados (DB_PATH) para buscar apenas bombas cujo intervalo de vazão
      (vazao_min e vazao_max) esteja dentro do intervalo global.
    - Converte a string dos coeficientes (armazenados em formato JSON) para um array NumPy.
    - Calcula os pontos de interseção entre a curva do sistema e a curva da bomba, considerando somente os
      pontos de interseção que estejam dentro do intervalo suportado pela bomba.
    - Retorna os dados (marca, modelo, diametro, rotacao) e os pontos de interseção encontrados, além dos coeficientes
      de head, eficiência, NPSHr e potência.
    - Caso não haja nenhuma bomba no intervalo de vazão selecionado, retorna a mensagem:
      "Não há nenhuma bomba para o intervalo de vazão selecionado"
"""

import sqlite3
import numpy as np
import json

# Caminho do banco de dados
DB_PATH = "./src/db/pump_data.db"

def parse_coef_string(coef_str: str) -> np.ndarray:
    """
    Converte uma string de coeficientes em formato JSON para um array NumPy.

    Exemplo de string JSON:
        "[-2.26728332e-10, 1.84845669e-08, -5.71944041e-07, 3.32206969e-04,
          1.57151363e-04, 5.70842371e+00]"
    
    Parâmetros:
        coef_str (str): String contendo os coeficientes.
        
    Retorna:
        np.ndarray: Array de floats com os coeficientes.
    """
    try:
        coef_list = json.loads(coef_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Erro ao decodificar JSON: {e}")
    
    return np.array(coef_list)

def find_intersection_points(coef_system: np.ndarray, coef_pump: np.ndarray,
                             global_min_flow: float, global_max_flow: float, tol: float = 1e-6) -> np.ndarray:
    """
    Encontra os pontos de interseção entre a curva do sistema e a curva da bomba.

    A interseção é definida pelos pontos x onde:
        poly_system(x) - poly_pump(x) == 0
    São consideradas apenas raízes reais que estejam dentro do intervalo global.

    Parâmetros:
        coef_system (np.ndarray): Coeficientes do polinômio do sistema.
        coef_pump (np.ndarray): Coeficientes do polinômio da bomba.
        global_min_flow (float): Fluxo mínimo do intervalo global.
        global_max_flow (float): Fluxo máximo do intervalo global.
        tol (float): Tolerância para considerar a parte imaginária como zero.
    
    Retorna:
        np.ndarray: Array com os pontos de interseção válidos.
    """
    # Calcula o polinômio diferença: f(x) = poly_system(x) - poly_pump(x)
    diff_coef = np.array(coef_system) - np.array(coef_pump)
    # Calcula as raízes do polinômio diferença
    roots = np.roots(diff_coef)
    
    # Filtra raízes reais que estejam no intervalo global
    valid_roots = []
    for root in roots:
        if np.abs(root.imag) < tol:
            real_root = root.real
            if global_min_flow <= real_root <= global_max_flow:
                valid_roots.append(real_root)
    
    return np.array(valid_roots)

def auto_pump_selection(coef_system_curve: np.ndarray, target_flow: float):
    """
    Seleciona os modelos de bomba cujas curvas de desempenho (coef_head) se interceptam com a curva do sistema.

    Apenas bombas cujo intervalo de vazão (vazao_min e vazao_max) esteja dentro do intervalo especificado
    e que possuam pontos de interseção entre seus próprios limites são consideradas.

    Parâmetros:
        coef_system_curve (np.ndarray): Coeficientes do polinômio do sistema (grau 5).
        target_flow (float): Vazão alvo para seleção de bombas.
    
    Retorna:
        list ou str: Lista de dicionários contendo os dados da bomba, os pontos de interseção e os
                     valores calculados de eficiência, NPSHr e potência (como float),
                     ou uma mensagem caso não haja nenhuma bomba para o intervalo selecionado.
    """
    results = []
    
    # Conecta ao banco de dados
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Query atualizada com a estrutura correta de colunas
        query = """
        SELECT marca, modelo, diametro, rotacao, estagios, vazao_min, vazao_max, 
               coef_head, coef_eff, coef_npshr, coef_power, 
               eff_bop, eff_bop_flow, p80_eff_bop_flow, p110_eff_bop_flow
        FROM pump_models
        WHERE p110_eff_bop_flow >= ? AND p80_eff_bop_flow <= ?
        """
        cursor.execute(query, (target_flow, target_flow))
        pump_models = cursor.fetchall()
        
        # Se nenhum registro for retornado, indica que não há bombas para o intervalo selecionado
        if not pump_models:
            return "Não há nenhuma bomba para o intervalo de vazão selecionado"
        
        # Processa cada bomba
        for pump in pump_models:
            marca, modelo, diametro, rotacao, estagios, pump_vazao_min, pump_vazao_max, coef_head_str, \
            coef_eff_str, coef_npshr_str, coef_power_str, pump_eff_bop, pump_eff_bop_flow, \
            pump_p80_eff_bop_flow, pump_p110_eff_bop_flow = pump
            
            print(coef_head_str)
            # Converte as strings de coeficientes para arrays NumPy
            try:
                coef_pump = parse_coef_string(coef_head_str)
                coef_eff = parse_coef_string(coef_eff_str)
                coef_npshr = parse_coef_string(coef_npshr_str)
                coef_power = parse_coef_string(coef_power_str)
            except Exception as e:
                print(f"Erro ao converter coeficientes para o modelo {modelo}: {e}")
                continue
            
            # Calcula os pontos de interseção entre a curva do sistema e a curva da bomba
            intersection_points = find_intersection_points(coef_system_curve, coef_pump,
                                                          pump_p80_eff_bop_flow, pump_p110_eff_bop_flow)
            # Filtra os pontos para que estejam dentro do intervalo suportado pela bomba
            intersection_points = intersection_points[
                (intersection_points >= pump_vazao_min) & (intersection_points <= pump_vazao_max)
            ]
            
            # Se houver pontos de interseção válidos, utiliza o primeiro ponto para calcular os valores
            if intersection_points.size > 0:
                x_val = float(intersection_points[0])
                y_val = float(np.polyval(coef_system_curve, x_val))
                intersections = [[x_val], [y_val]]
                
                # Calcula os valores de eficiência, NPSHr e potência para o ponto de interseção escolhido
                pump_eff = float(np.polyval(coef_eff, x_val))
                pump_npshr = float(np.polyval(coef_npshr, x_val))
                pump_power = float(np.polyval(coef_power, x_val))
                
                results.append({
                    "marca": marca,
                    "modelo": modelo,
                    "diametro": diametro,
                    "rotacao": rotacao,
                    "estagios": estagios,
                    "intersecoes": intersections,
                    "pump_coef_head": coef_pump,
                    "pump_coef_eff": coef_eff,
                    "pump_coef_npshr": coef_npshr,
                    "pump_coef_power": coef_power,
                    "pump_vazao_min": pump_vazao_min,
                    "pump_vazao_max": pump_vazao_max,
                    "pump_eff": pump_eff,
                    "pump_npshr": pump_npshr,
                    "pump_power": pump_power
                })
    finally:
        cursor.close()
        conn.close()
    
    return results



# Exemplo de uso
# if __name__ == '__main__':
#     # Exemplo de coeficientes do sistema (polinômio de grau 5)
#     coef_system_curve = np.array([
#         -2.26728332e-10, 1.84845669e-08, -5.71944041e-07,
#         3.32206969e-04, 1.57151363e-04, 5.70842371e+00
#     ])
#     
#     # Define o intervalo global de fluxo desejado
#     global_min_flow = 0.0
#     global_max_flow = 100.0  # Ajuste conforme necessário
#     
#     # Chama a função para selecionar as bombas
#     pumps_found = auto_pump_selection(coef_system_curve, global_min_flow, global_max_flow)
#     
#     # Exibe os resultados
#     if isinstance(pumps_found, str):
#         # Caso não haja nenhuma bomba no intervalo
#         print(pumps_found)
#     elif pumps_found:
#         print("Bombas encontradas com interseção:")
#         for pump in pumps_found:
#             print(f"Marca: {pump['marca']}, Modelo: {pump['modelo']}, "
#                   f"Diâmetro: {pump['diametro']}, Rotação: {pump['rotacao']}")
#             print(f"Ponto(s) de interseção (x, y): {pump['intersecoes']}\n")
#     else:
#         print("Nenhum modelo de bomba apresentou interseção no intervalo especificado.")
