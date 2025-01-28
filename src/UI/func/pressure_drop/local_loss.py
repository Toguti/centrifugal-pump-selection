import pandas as pd
import numpy as np

dt_equiv_lenght = pd.read_csv("./src/db/eq_lenght_exported.csv", sep=";", decimal=',', index_col=0)

def get_size_singularities_loss_values(size):
    print(dt_equiv_lenght)
    print(type(dt_equiv_lenght.index[0]))
    print(type(np.int64(size)))
    return dt_equiv_lenght.loc[np.int64(size)].to_numpy()

# options = ['ct_90_rl', 
#            'ct_90_rm', 
#            'ct_90_rc', 
#            'ct_45', 
#            'cur_90_1_1-2', 
#            'cur_90_1', 
#            'cur_45', 
#            'ent_norm', 
#            'ent_borda', 
#            'rg_ga_a', 
#            'rg_gb_a', 
#            'rg_an_a', 
#            'te_main', 
#            'te_deriv', 
#            'te_div', 
#            'val_pec', 
#            'sai_can', 
#            'valv_ret_leve', 
#            'valv_ret_pesado']

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
size_dict_internal_diameter_sch40 = {
    "13 (1/2\")": 15.80,
    "19 (3/4\")": 20.93,
    "25 (1\")": 26.64,
    "32 (1.1/4\")": 35.04,
    "38 (1.1/2\")": 40.90,
    "50 (2\")": 52.51,
    "63 (2.1/2\")": 62.71,
    "75 (3\")": 77.92,
    "100 (4\")": 102.26,
    "125 (5\")": 128.20,
    "150 (6\")": 154.06,
    "200 (8\")": 202.72,
    "250 (10\")": 254.51,
    "300 (12\")": 303.23,
    "350 (14\")": 333.34,
}