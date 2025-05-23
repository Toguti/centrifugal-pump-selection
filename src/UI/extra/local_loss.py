import pandas as pd
import numpy as np

# Load the CSV table. Make sure the index corresponds to the size values.
dt_equiv_lenght = pd.read_csv("./src/db/eq_lenght_exported.csv", sep=";", decimal=',', index_col=0)

def get_size_singularities_loss_values(size):
    if size not in dt_equiv_lenght.index:
        raise ValueError(f"Size {size} not found in the CSV data.")
    current_size_row = dt_equiv_lenght.loc[size]
    # Adjust slicing below if needed in case the CSV columns order changes.
    return current_size_row[1:].to_numpy()

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
    "400 (16\")": 400,
    "500 (20\")": 500,
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
    "400 (16\")": 406.40,
    "500 (20\")": 508.00,
}
