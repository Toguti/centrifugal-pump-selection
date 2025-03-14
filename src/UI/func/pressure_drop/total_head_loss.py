import numpy as np
import matplotlib.pyplot as plt
from UI.func.pressure_drop.local_loss import size_dict_internal_diameter_sch40, size_dict, get_size_singularities_loss_values

def friction_factor(Re, roughness, D, tol=1e-6, max_iter=100):
    """
    Re: Reynolds number
    roughness: Absolute roughness of the pipe
    D: Diameter of the pipe
    tol: Tolerance for stopping criterion.
    max_iter: Maximum number of iterations.
    """
    epsilon = roughness / D  # Roughness relativo
    f = (1.14 + 2*np.log10(D/epsilon)) ** (-2)
    for _ in range(max_iter):
        f_new = (-2.0 * np.log10(epsilon / 3.7 + 2.51 / (Re * np.sqrt(f))))**-2
        if abs(f_new - f) < tol:
            return f_new
        f = f_new
    raise RuntimeError(f"Failed to converge after {max_iter} iterations.")

def pressure_loss(D, L, Q, mu, rho, g, h, K, roughness):
    """
    Calcula a perda de carga total em um trecho de tubulação.
    """
    A = np.pi * (D/2)**2 
    V = Q / A 
    Re = rho * V * D / mu 
    if Re < 2000:
        f = 64/Re
    else:
        f = friction_factor(Re, roughness, D) 
    h_f = f * L/D * V**2 / (2*g)
    h_s = K * V**2 / (2*g) 
    h_g = h 
    delta_p = (h_f + h_s + h_g)
    return delta_p  # em Pascals

def pressure_loss_array(D, L, Q, mu, rho, g, h, K, roughness):
    """
    Calcula a perda de carga para um array de vazões.
    """
    Q = Q/3600  # Converte de m³/h para m³/s
    A = np.pi * (D/2)**2 
    V = Q / A
    Re = rho * V * D / mu 
    laminar_flow, turbulent_flow = Re[Re<4000], Re[Re>=4000]
    f_lam = 64/laminar_flow
    f_turb = np.zeros(turbulent_flow.size)
    for i, value in enumerate(turbulent_flow):
        f_turb[i] = friction_factor(value, roughness, D)
    f = np.concatenate((f_lam, f_turb))
    h_f = f * L/D * V**2 / (2*g)
    h_s = f.size * K * V**2 / (2*g) 
    h_g = h * f.size
    h_total = (h_f + h_s + h_g)
    return h_total/(rho*g)

def calculate_pipe_system_head_loss(suction_array, suction_size, discharge_array, discharge_size, target_flow_value, mu, rho):
    """
    Calcula a curva de perda de carga do sistema e realiza um ajuste polinomial de grau 5.
    
    Retorna:
        head_values_coef: coeficientes do polinômio ajustado
        min_flow: valor mínimo da vazão (0)
        max_flow: valor máximo da vazão (target_flow_value * 1.40)
    """
    suction_array = np.array(suction_array)
    discharge_array = np.array(discharge_array)

    # Gera os valores de vazão de 0.001 até target_flow_value*1.40 (para evitar divisão por zero)
    flow_values_array = np.linspace(0.001, target_flow_value*1.40, int(target_flow_value*1.40/0.001))

    # Extrai os parâmetros do array de sucção
    suction_length = suction_array[0]
    suction_height = suction_array[1]
    suction_local_loss = suction_array[2:]

    # Extrai os parâmetros do array de descarga
    discharge_length = discharge_array[0]
    discharge_height = discharge_array[1]
    discharge_local_loss = discharge_array[2:]

    # Calcula os comprimentos totais de perdas locais equivalentes
    suction_total_local_loss_length = np.sum(get_size_singularities_loss_values(get_size_value(suction_size)))
    discharge_total_local_loss_length = np.sum(get_size_singularities_loss_values(get_size_value(discharge_size)))

    suction_total_linear_length = suction_total_local_loss_length + suction_length

    # Calcula a perda de carga para cada valor de vazão
    head_value_axis = pressure_loss_array(
        size_dict_internal_diameter_sch40[suction_size]/1000,
        suction_total_linear_length,
        flow_values_array,
        mu/1000,  # Ajuste da viscosidade
        rho,
        g=9.81,
        h=suction_height,
        K=0,
        roughness=0.000015
    )

    # Realiza o ajuste polinomial de grau 5
    head_values_coef = np.polyfit(flow_values_array, head_value_axis, 5)
    
    # Define os limites da vazão
    min_flow = 0
    max_flow = target_flow_value * 1.40

    return head_values_coef, min_flow, max_flow

def calculate_total_equivalent_length(local_loss_array_quantities):
    # Input: local_loss_array_quantities é um numpy array com as quantidades de perda local.
    None

def get_size_value(string_size):
    try:
        return size_dict[string_size]
    except TypeError:
        print("Erro na transformação do valor de string para inteiro no size_value.")
