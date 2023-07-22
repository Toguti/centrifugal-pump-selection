import pandas as pd

dt_equiv_lenght = pd.read_excel("./src/data/eq_lenght_exported.xlsx", decimal=',')

print(dt_equiv_lenght)

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



diameter = dt_equiv_lenght["d_pol"].values
quant = [0]*len(options)
size = [0]*len(options)
