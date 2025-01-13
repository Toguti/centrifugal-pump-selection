import numpy as np
import matplotlib.pyplot as plt
from UI.func.pressure_drop.local_loss import size_dict, get_singularity_value

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
    print("Re ", Re)
    for _ in range(max_iter):
        f_new = (-2.0 * np.log10(epsilon / 3.7 + 2.51 / (Re * np.sqrt(f))))**-2
        print(_, f_new)
        if abs(f_new - f) < tol:
            return f_new
        f = f_new
    print(f)

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

    # Area of cross-section
    A = np.pi * (D/2)**2 
 
    # Velocity
    V = Q / A
    print(rho)

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

    return h_total  # in Pascals

def plotSystemPoint(data):
    flow_data = []
    total_head = 0
    for el in data:
        component = el[1]
        c_size = el[2]
        quantity = el[3]
        flow = el[4]
        flow_data.append(flow)
        total_head += pressure_loss(size_dict[c_size]/1000, get_singularity_value(size_dict[c_size],component) * quantity , flow/3600, 0.001, 1000, 9.81, 0, 0, 0.00015) 
        print(component, c_size, quantity, flow)
    plt.plot(max(flow_data), total_head, marker='o')  # Multiply flow rates by 3600 to convert back to m^3/h for the plot
    plt.xlabel('Volumetric flow rate (m^3/h)')
    plt.ylabel('Total head loss (m)')
    plt.title('Head loss vs Flow rate for a circular pipe')
    plt.grid(True)
    plt.show()


def plotCurve(data, max_flow, fluid_properties, delta_h=0, roughness= 0.0015):
    flow_rates = np.linspace(0.0001, round(max_flow*1.2), 100) / 3600
    total_head_loss = np.zeros(shape=(len(data), flow_rates.size))
    for idx, el in enumerate(data):
        component = el[1]
        c_size = el[2]
        quantity = el[3]
        total_head_loss[idx] = pressure_loss_array(size_dict[c_size]/1000, 
                            get_singularity_value(size_dict[c_size],component)*quantity,
                            flow_rates, 
                            fluid_properties['mu'], 
                            fluid_properties['rho'], 
                            9.81,
                            0,
                            delta_h,roughness)
    total_head_loss = np.sum(total_head_loss, axis=0)
    plt.plot(flow_rates*3600, total_head_loss)
    plt.xlabel('Volumetric flow rate (m^3/h)')
    plt.ylabel('Total head loss (m)')
    plt.title('Head loss vs Flow rate for a circular pipe')
    plt.grid(True)
    plt.show()

size_dict = {
    "13 (1/2\")": 13,
    "19 (3/4\")": 19,
    "25 (1\")": 25,
    "32 (1.1/4\")": 32,
    "38 (1.1/2\")": 38,
    "50 (2\")": 50,
    "63 (2.1/2\")": 63,
    "75 (3\")": 75,
    "100 (4\")": 100,
    "125 (5\")": 125,
    "150 (6\")": 150,
    "200 (8\")": 200,
    "250 (10\")": 250,
    "300 (12\")": 300,
    "350 (14\")": 350,
}