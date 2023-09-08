import pandas as pd

dt_equiv_lenght = pd.read_csv("./src/data/eq_lenght_exported.csv", sep=";", decimal=',', index_col=0)

type(dt_equiv_lenght)
# print(dt_equiv_lenght)



def get_singularity_value(size, element):
    return dt_equiv_lenght.loc[size,element]

def sum_equivalent_length(data):
    total = 0
    for el in data:
        total += get_singularity_value(size_dict[el[2]],el[1])*el[3]
    print("Soma de perda Equivalente")
    return total

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

print(dt_equiv_lenght)
print(dt_equiv_lenght.dtypes)

