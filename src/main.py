import matplotlib.pyplot as plt
import numpy as np
import scipy.constants as sc
from pressure_drop.pressure_loss import pressure_loss
from CoolProp.CoolProp import PropsSI

D = 0.05  # Diameter of the pipe[m]
L = 100  # Length of the pipe [m]
T_user = 25 # Fluid Temperature [C]
P_user = 101325 # Fluid Pressure [Pa]
rho = PropsSI('D', 'T', (T_user+273.15), 'P', P_user, 'INCOMP::Water')/1000 # Densidade [kg/m^3]
mu = PropsSI('V', 'T', (T_user+273.15), 'P', P_user, 'INCOMP::Water') # Viscosidade [cP or g/cm.s]
g = sc.g  # Acceleration due to gravity
h = 10  # Height difference between start and end of the pipe
K = 2  # Total loss coefficient for fittings and valves
roughness = 0.0003  # Roughness of the pipe

print(rho, mu)

# Create a range of flow rates from 0.1 to 10 m^3/h in increments of 0.1, then convert to m^3/s
flow_rates = np.linspace(5, 500, 10) / 3600

# Calculate the corresponding pressure losses
head_losses = [pressure_loss(D, L, Q, mu, rho, g, h, K, roughness)/rho/g for Q in flow_rates]

# Plot
plt.plot(flow_rates * 3600, head_losses)  # Multiply flow rates by 3600 to convert back to m^3/h for the plot
plt.xlabel('Volumetric flow rate (m^3/h)')
plt.ylabel('Total head loss (m)')
plt.title('Head loss vs Flow rate for a circular pipe')
plt.grid(True)
plt.show()