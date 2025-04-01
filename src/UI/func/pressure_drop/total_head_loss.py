import numpy as np
import matplotlib.pyplot as plt
from UI.extra.local_loss import size_dict_internal_diameter_sch40, size_dict, get_size_singularities_loss_values

def friction_factor(Re, roughness, D, tol=1e-6, max_iter=100):
    """
    Calcula o fator de atrito para fluxo turbulento utilizando o método iterativo.
    
    Parâmetros:
        Re: Número de Reynolds
        roughness: Rugosidade absoluta da tubulação (m)
        D: Diâmetro da tubulação (m)
        tol: Tolerância para o critério de convergência
        max_iter: Número máximo de iterações
    
    Retorna:
        Fator de atrito (f)
    """
    epsilon = roughness / D
    f = (1.14 + 2*np.log10(D/epsilon)) ** (-2)
    for _ in range(max_iter):
        f_new = (-2.0 * np.log10(epsilon / 3.7 + 2.51 / (Re * np.sqrt(f))))**-2
        if abs(f_new - f) < tol:
            return f_new
        f = f_new
    raise RuntimeError(f"Failed to converge after {max_iter} iterations.")


def pressure_loss(D, L, Q, mu, rho, g, h, K, roughness):
    """
    Calcula a perda de carga total (em metros de coluna de fluido) para um trecho de tubulação,
    considerando o comprimento linear, a perda por singularidades e a elevação.

    Parâmetros:
        D: Diâmetro interno da tubulação (m)
        L: Comprimento linear total da tubulação (m), podendo incluir o comprimento equivalente das singularidades
        Q: Vazão em m³/h (pode ser um escalar ou array)
        mu: Viscosidade dinâmica (Pa.s)
        rho: Densidade (kg/m³)
        g: Aceleração da gravidade (m/s²)
        h: Diferença de elevação (m)
        K: Fator de perda local. Pode ser um escalar (soma dos K) ou um array de fatores individuais.
        roughness: Rugosidade absoluta da tubulação (m)
    
    Retorna:
        Perda de carga total (em metros de coluna de fluido) para cada valor de vazão.
    """
    # Converte a vazão de m³/h para m³/s e garante que Q seja um array para facilitar a vetorização
    Q = np.atleast_1d(Q) / 3600.0

    # Calcula a área da seção transversal (m²)
    A = np.pi * (D / 2)**2

    # Velocidade média do fluido (m/s)
    V = Q / A

    # Número de Reynolds
    Re = (rho * V * D) / mu

    # Cálculo do fator de atrito para cada valor de Re, usando critério unificado: Re < 2000 é laminar
    f = np.array([
        64 / Re_i if Re_i < 2000 else friction_factor(Re_i, roughness, D)
        for Re_i in Re
    ])

    # Perda de carga por atrito (m)
    h_f = f * (L / D) * (V**2) / (2 * g)

    # Se K for array, soma os fatores; se for escalar, utiliza-o diretamente
    total_K = np.sum(K) if np.ndim(K) > 0 else K

    # Perda de carga por singularidades (m)
    h_s = total_K * (V**2) / (2 * g)

    # Perda de carga de elevação (m)
    h_g = h

    # Perda de carga total (m)
    h_total = h_f + h_s + h_g

    # Retorna escalar se a entrada era um único valor de vazão
    return h_total[0] if h_total.size == 1 else h_total

def calculate_pipe_system_head_loss(suction_array, suction_size, discharge_array, discharge_size, target_flow_value, mu, rho, roughness):
    """
    Calcula a curva de perda de carga do sistema considerando:
        - Trecho de sucção: inclui comprimento físico, perdas locais (singularidades) e elevação.
        - Trecho de descarga: inclui comprimento físico, perdas locais (singularidades) e elevação.
    Realiza o ajuste polinomial de grau 5 da perda total x vazão.

    Parâmetros:
        suction_array: [comprimento_sucção, altura_sucção, ...perdas_locais_sucção]
        suction_size: chave para obter diâmetro e equivalência (ex.: "25 (1\")")
        discharge_array: [comprimento_descarga, altura_descarga, ...perdas_locais_descarga]
        discharge_size: chave para obter diâmetro e equivalência (ex.: "25 (1\")")
        target_flow_value: valor máximo de vazão (m³/h) para a curva
        mu: viscosidade dinâmica (em unidades compatíveis, lembrando o ajuste)
        rho: densidade (kg/m³)
        roughness: rugosidade absoluta da tubulação (m)
    
    Retorna:
        head_values_coef: coeficientes do polinômio ajustado (grau 5)
        min_flow: vazão mínima (0)
        max_flow: vazão máxima (target_flow_value * 1.40)
        suction_friction_loss: perda de carga na sucção para a vazão de projeto (m)
        suction_height: altura de sucção (m) - valor do segundo elemento do suction_array
    """
    import numpy as np

    # Converte as entradas para arrays
    suction_array = np.array(suction_array)
    discharge_array = np.array(discharge_array)

    # Gera um array de vazões (m³/h) de 0.001 até target_flow_value * 1.40 (evitando divisão por zero)
    n_max_points = 1000 
    n_points = min(int(target_flow_value * 1.40 / 0.001), n_max_points)
    flow_values_array = np.linspace(0.001, target_flow_value * 1.40, n_points)


    # --- Extração dos parâmetros de sucção ---
    suction_length = suction_array[0]
    suction_height = suction_array[1]
    suction_local_loss = suction_array[2:]  # perdas locais fornecidas pelo usuário

    # --- Extração dos parâmetros de descarga ---
    discharge_length = discharge_array[0]
    discharge_height = discharge_array[1]
    discharge_local_loss = discharge_array[2:]  # perdas locais fornecidas pelo usuário

    # --- Comprimento equivalente das singularidades baseado no diâmetro padrão ---
    suction_eq_loss = np.sum(get_size_singularities_loss_values(get_size_value(suction_size)))
    discharge_eq_loss = np.sum(get_size_singularities_loss_values(get_size_value(discharge_size)))

    # --- Comprimento efetivo de cada trecho ---
    # Soma do comprimento físico, perdas equivalentes (padrão) e perdas locais (informadas)
    L_eff_suction = suction_length + suction_eq_loss + np.sum(suction_local_loss)
    L_eff_discharge = discharge_length + discharge_eq_loss + np.sum(discharge_local_loss)

    # --- Diâmetros internos (convertendo de mm para m) ---
    D_suction = size_dict_internal_diameter_sch40[suction_size] / 1000
    D_discharge = size_dict_internal_diameter_sch40[discharge_size] / 1000

    # --- Cálculo das perdas de carga para cada trecho ---
    # Utiliza a função pressure_loss_array (já adaptada para operar com array de vazões)
    head_loss_suction = pressure_loss(
        D_suction,
        L_eff_suction,
        flow_values_array,
        mu / 1000,    # ajuste da viscosidade, conforme padrão anterior
        rho,
        g=9.81,
        h=suction_height,
        K=0,          # K = 0 se todas as perdas locais já forem convertidas em comprimento equivalente 
        roughness=roughness
        )

    head_loss_discharge = pressure_loss(
        D_discharge,
        L_eff_discharge,
        flow_values_array,
        mu / 1000,
        rho,
        g=9.81,
        h=discharge_height,
        K=0,
        roughness=roughness
        )

    # --- Perda de carga total do sistema ---
    total_head_loss = head_loss_suction + head_loss_discharge

    # --- Ajuste polinomial de grau 5 ---
    head_values_coef = np.polyfit(flow_values_array, total_head_loss, 5)

    # Define os limites de vazão
    min_flow = 0
    max_flow = target_flow_value * 1.40
    
    # Calcular a perda de carga na sucção para a vazão de projeto
    # Garantindo que o resultado seja tratado corretamente, independentemente se é escalar ou array
    suction_friction_loss_result = pressure_loss(
        D_suction,
        L_eff_suction,
        np.array([target_flow_value]),
        mu / 1000,
        rho,
        g=9.81,
        h=0,  # Desconsiderar elevação para obter apenas a perda por fricção
        K=0,
        roughness=roughness
    )
    
    # Use np.atleast_1d para garantir que seja tratado como array, mesmo que seja escalar
    suction_friction_loss = np.atleast_1d(suction_friction_loss_result)[0]

    return head_values_coef, min_flow, max_flow, suction_friction_loss, suction_height

def calculate_total_equivalent_length(local_loss_array_quantities):
    # Input: local_loss_array_quantities é um numpy array com as quantidades de perda local.
    None

def get_size_value(string_size):
    try:
        return size_dict[string_size]
    except TypeError:
        print("Erro na transformação do valor de string para inteiro no size_value.")
