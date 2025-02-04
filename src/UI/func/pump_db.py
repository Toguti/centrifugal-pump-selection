import sqlite3
import json
import numpy as np
import os

# Caminho do banco de dados
db_path = "./src/db/pump_data.db"

# Criar conexão e cursor
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Criar tabela de bombas se não existir
cursor.execute("""
    CREATE TABLE IF NOT EXISTS bombas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        modelo TEXT NOT NULL,
        rotacao INTEGER NOT NULL,
        vazao_min REAL NOT NULL,
        vazao_max REAL NOT NULL,
        coef_head TEXT NOT NULL,
        coef_eff TEXT NOT NULL,
        coef_npshr TEXT,
        coef_power TEXT NOT NULL
    )
""")

# Função para gerar coeficientes polinomiais aleatórios para teste


# Função para adicionar uma bomba ao banco de dados
def adicionar_bomba(modelo, rotacao, vazao_min, vazao_max, coef_head, coef_eff, coef_npshr, coef_power):
    
    cursor.execute("""
        INSERT INTO bombas (modelo, rotacao, vazao_min, vazao_max, coef_head, coef_eff, coef_npshr, coef_power)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (modelo, rotacao, vazao_min, vazao_max, coef_head, coef_eff, coef_npshr, coef_power))
    
    conn.commit()

# Adicionar bombas fictícias se a tabela estiver vazia
cursor.execute("SELECT COUNT(*) FROM bombas")
if cursor.fetchone()[0] == 0:
    bombas_teste = [
        ("MEGANORM-25-200", 
         3500, 
         0.12, 
         18, 
         [1.6203366293119338e-05, -0.0006504262846409288, 0.007837100137631333, -0.10339741918416842, 0.11683996767802679, 94.15548733348413],
         [-0.0007761887470387009, 0.033911048199121115, -0.5576200263934282, 4.241235763784843, -15.590336323464351, 115.48640858022397],
         [-5.9633593936612955e-05, 0.003076816279138715, -0.059727118368036666, 0.5692279008187227, -2.4263270913352737, 4.095657732597875],
         [1.1285529591079345e-05, -0.00046960392949810037, 0.007490625515566242, -0.05418332751654858, 0.46983129211803865, 3.078216968283303])
    ]
    
    for bomba in bombas_teste:
        adicionar_bomba(*bomba)

print("Banco de dados criado com sucesso!")

# Fechar conexão
conn.close()
