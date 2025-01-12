from pyfluids import *


for i,j in enumerate(FluidsList):
    print(i,j)


def fluidProp(T_user=25, P_user=101325, fluid='INCOMP::Water'):

    # Fluid Data from Props SI
    fluid_data = {'rho':PropsSI('D', 'T', (T_user+273.15), 'P', P_user, fluid), 'mu': PropsSI('V', 'T', (T_user+273.15), 'P', P_user, fluid)}
    return fluid_data