import numpy as np
import matplotlib.pyplot as plt
from UI.func.pressure_drop.local_loss import size_dict_internal_diameter_sch40, size_dict, get_size_singularities_loss_values

## Friction Factor - Uses the Colebrook equation for 

def friction_factor(Re, roughness, D, tol=1e-6, max_iter=100):
    """
    Re: Reynolds number
    roughness: Absolute roughness of the pipe
    D: Diameter of the pipe
    tol: Tolerance for stopping criterion.
    max_iter: Maximum number of iterations=
    """
    # Initial guess (Churchill's formula)
    epsilon = roughness / D  # Relative roughness

    # f = (8*((8/Re)**12 + (2.457*np.log(1/((7/Re)**0.9 + 0.27*(epsilon))))**1.5)**(1/12))**2
    f = (1.14 + 2*np.log10(D/epsilon)) ** (-2)

    # Simple Fixed-Point Iteration
    for _ in range(max_iter):
        f_new = (-2.0 * np.log10(epsilon / 3.7 + 2.51 / (Re * np.sqrt(f))))**-2

        if abs(f_new - f) < tol:
            return f_new
        f = f_new


    # If the method didn't converge
    raise RuntimeError(f"Failed to converge after {max_iter} iterations.")


def pressure_loss(D, L, Q, mu, rho, g, h, K, roughness):
    """
    D: Diameter of the pipe (m)
    L: Length of the pipe (m)
    Q: Volumetric flow rate (m^3/s)
    mu: Dynamic viscosity (Pa.s)
    rho: Density (kg/m^3)
    g: Acceleration due to gravity (m/s^2)
    h: Height difference between start and end of pipe (m)
    K: Total loss coefficient for fittings and valves (dimensionless)
    roughness: Absolute roughness of the pipe (m)
    """

    # Area of cross-section
    A = np.pi * (D/2)**2 

    # Velocity
    V = Q / A 

    # Reynolds number
    Re = rho * V * D / mu 

    if Re < 2000:
        f = 64/Re
    else:
        # Friction factor using the colebrook equation
        f = friction_factor(Re, roughness, D) 



    # Distributed losses (Darcy-Weisbach equation)
    h_f = f * L/D * V**2 / (2*g)

    # Singularity losses
    h_s = K * V**2 / (2*g) 

    # Pressure loss due to change in height
    h_g = h 

    # Total pressure loss
    delta_p = (h_f + h_s + h_g)

    return delta_p  # in Pascals

def pressure_loss_array(D, L, Q, mu, rho, g, h, K, roughness):
    """
    D: Diameter of the pipe (m)
    L: Length of the pipe (m)
    Q: Volumetric flow rate (m^3/s)
    mu: Dynamic viscosity (Pa.s)
    rho: Density (kg/m^3)
    g: Acceleration due to gravity (m/s^2)
    h: Height difference between start and end of pipe (m)
    K: Total loss coefficient for fittings and valves (dimensionless)
    roughness: Absolute roughness of the pipe (m)
    """
    Q = Q/3600
    # Area of cross-section
    A = np.pi * (D/2)**2 
 
    # Velocity
    V = Q / A

    # Reynolds number
    Re = rho * V * D / mu 

    # Split Values into turbulent and laminar flow
    laminar_flow, turbulent_flow = Re[Re<4000], Re[Re>=4000]
    f_lam = 64/laminar_flow
    f_turb = np.zeros(turbulent_flow.size)

    # Friction factor for each value of flow
    for i, value in enumerate(turbulent_flow):
        f_turb[i] = friction_factor(value, roughness, D)


    f = np.concatenate((f_lam, f_turb))

    # Distributed losses (Darcy-Weisbach equation)
    h_f = f * L/D * V**2 / (2*g)

    # Singularity losses
    h_s = f.size * K * V**2 / (2*g) 

    # Pressure loss due to change in height
    h_g = h * f.size

    # Total pressure loss
    h_total = (h_f + h_s + h_g)
 
    return h_total/(rho*g)  # in Pascals




def calculate_pipe_system_head_loss(suction_array, suction_size, discharge_array, discharge_size, target_flow_value, mu, rho):
    # Tranformar em array numpy
    suction_array = np.array(suction_array)
    discharge_array = np.array(discharge_array)

    # Estabelecer o intervalo de vazão a ser calculado

    flow_values_array = np.linspace(0.001, target_flow_value*1.40, int(target_flow_value*1.40/0.001))

    # Separar os valores
    suction_length = suction_array[0]          # Pega o primeiro valor (index 0)
    suction_height = suction_array[1]         # Pega o segundo valor (index 1)
    suction_local_loss = suction_array[2:]    # Pega os valores a partir do index 2 até o final
    print(suction_length)
    ## Separa os valores discharge
    discharge_length = discharge_array[0]          # Pega o primeiro valor (index 0)
    discharge_height = discharge_array[1]         # Pega o segundo valor (index 1)
    discharge_local_loss = discharge_array[2:]    # Pega os valores a partir do index 2 até o final

    # Calcular o comprimento total de perda de carga equivalente das perdas localizadas
    print(get_size_value(suction_size))
    print(get_size_value(discharge_size))
    suction_total_local_loss_length = np.sum(get_size_singularities_loss_values(get_size_value(suction_size)))
    discharge_total_local_loss_length = np.sum(get_size_singularities_loss_values(get_size_value(discharge_size)))

    suction_total_linear_length = suction_total_local_loss_length + suction_length

    head_value_axis = pressure_loss_array(size_dict_internal_diameter_sch40[suction_size]/1000,
                                          suction_total_linear_length,
                                          flow_values_array,
                                          mu/1000, #
                                          rho, #
                                          g=9.81, #
                                          h=suction_height, #
                                          K=0, # Perdas localizadas em K
                                          roughness=0.000015) #

    print(head_value_axis)


def calculate_total_equivalent_length(local_loss_array_quantities):
    # Input local_loss_array_quantities is a numpy array containing quantities of local loss based on no
    None

def get_size_value(string_size):
    try:
        return size_dict[string_size]
    except TypeError:
        print("Erro na transformação do valor de string para inteiro no size_value.")
    