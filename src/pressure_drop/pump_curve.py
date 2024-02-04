import json
import os

'''
Data 
[{
Modelo: ;
RPM: ;
Diametro: ;
Vazao: ;
Head: ;
Pot: ;
NPSHr: ;
EFF: ;
}]
'''



def plotPumpCurve():
    with open('./src/db/pumps/pump_data.json', 'r') as f:
        data = json.load(f)
        print(data)

plotPumpCurve()

