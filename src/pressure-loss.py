import numpy as np
import scipy.constants as sc

## Friction Factor - Uses the Colebrook equation for 

def friction_factor(Re, roughness, D, tol=1e-6, max_iter=1000):
    """
    Re: Reynolds number
    roughness: Absolute roughness of the pipe
    D: Diameter of the pipe
    tol: Tolerance for stopping criterion.
    max_iter: Maximum number of iterations
    """
    # Initial guess (Churchill's formula)
    f = (8*((8/Re)**12 + (2.457*np.log(1/((7/Re)**0.9 + 0.27*(roughness/D))))**1.5)**(1/12))**2
    epsilon = roughness / D  # Relative roughness

    # Simple Fixed-Point Iteration
    for _ in range(max_iter):
        f_new = (-2.0 * np.log10(epsilon / 3.7 + 2.51 / (Re * np.sqrt(f))))**-2
        if abs(f_new - f) < tol:
            return f_new
        f = f_new

    # If the method didn't converge
    raise RuntimeError(f"Failed to converge after {max_iter} iterations.")

# Example usage:
f = friction_factor(Re=1e5, roughness=0.0000015, D=0.05)
print(f"Friction factor: {f}")

##

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

    # Friction factor using the colebrook equation
    f = friction_factor(Re, roughness, D) 

    # Distributed losses (Darcy-Weisbach equation)
    h_f = f * L/D * V**2 / (2*g)

    # Singularity losses
    h_s = K * V**2 / (2*g) 

    # Pressure loss due to change in height
    h_g = h 

    # Total pressure loss
    delta_p = rho * g * (h_f + h_s + h_g)

    return delta_p  # in Pascals

# Example usage:
delta_p = pressure_loss(D=0.05, L=100, Q=0.02, mu=1e-3, rho=1000, g=sc.g, h=10, K=2, roughness=0.0000015)
print(f"Pressure loss: {delta_p/1e5} bar")