import pandas as pd
from pressure_drop.pressure_loss import pressure_loss
import matplotlib.pyplot as plt
dt_equiv_lenght = pd.read_csv("./src/db/eq_lenght_exported.csv", sep=";", decimal=',', index_col=0)

type(dt_equiv_lenght)
# print(dt_equiv_lenght)



def get_singularity_value(size, element):
    
    return dt_equiv_lenght.loc[size,element]

def sum_equivalent_length(data):
    total = {}
    for el in data:
        if el[2] in total:
            total[el[2]] += get_singularity_value(size_dict[el[2]],el[1])*el[3]
        else:
            total[el[2]] = get_singularity_value(size_dict[el[2]],el[1])*el[3]
    return total

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
options = ['ct_90_rl', 
           'ct_90_rm', 
           'ct_90_rc', 
           'ct_45', 
           'cur_90_1_1-2', 
           'cur_90_1', 
           'cur_45', 
           'ent_norm', 
           'ent_borda', 
           'rg_ga_a', 
           'rg_gb_a', 
           'rg_an_a', 
           'te_main', 
           'te_deriv', 
           'te_div', 
           'val_pec', 
           'sai_can', 
           'valv_ret_leve', 
           'valv_ret_pesado']

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