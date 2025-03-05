import sqlite3
import json
import numpy as np
import os

# Caminho do banco de dados
db_path = "./src/db/pump_data.db"

# Criar conexão e cursor
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Criar tabela de pump_models se não existir
cursor.execute("""
    CREATE TABLE IF NOT EXISTS pump_models (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT NOT NULL,
        modelo TEXT NOT NULL,
        diametro TEXT NOT NULL,
        rotacao INTEGER NOT NULL,
        vazao_min REAL NOT NULL,
        vazao_max REAL NOT NULL,
        coef_head TEXT NOT NULL,
        coef_eff TEXT NOT NULL,
        coef_npshr TEXT NOT NULL,
        coef_power TEXT NOT NULL,
        UNIQUE(marca, modelo, diametro, rotacao)
    )
""")

# Função para gerar coeficientes polinomiais aleatórios para teste


# Função para adicionar uma bomba ao banco de dados
def adicionar_bomba(marca, modelo, diametro, rotacao, vazao_min, vazao_max, coef_head, coef_eff, coef_npshr, coef_power):
    """
    Insere uma bomba no banco de dados apenas se não existir uma com os mesmos identificadores:
    marca, modelo, diâmetro e rotação.

    Caso já exista, a função apenas retorna sem inserir.
    """
    # Verifica se já existe um registro com os mesmos identificadores
    cursor.execute("""
        SELECT 1 FROM pump_models
        WHERE marca = ? AND modelo = ? AND diametro = ? AND rotacao = ?
    """, (marca, modelo, diametro, rotacao))
    
    if cursor.fetchone() is not None:
        # Registro já existe, então não insere e pode exibir uma mensagem de log, se desejado
        print("Registro já existe. Inserção cancelada.")
        return

    # Converte os coeficientes para o formato JSON
    coef_head_json = json.dumps(coef_head)
    coef_eff_json = json.dumps(coef_eff)
    coef_npshr_json = json.dumps(coef_npshr)
    coef_power_json = json.dumps(coef_power)

    # Insere o novo registro no banco de dados
    cursor.execute("""
        INSERT INTO pump_models (marca, modelo, diametro, rotacao, vazao_min, vazao_max, coef_head, coef_eff, coef_npshr, coef_power)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (marca, modelo, diametro, rotacao, vazao_min, vazao_max,
          coef_head_json, coef_eff_json, coef_npshr_json, coef_power_json))
    
    conn.commit()
    print("Registro inserido com sucesso!")

# Adicionar pump_models fictícias se a tabela estiver vazia
cursor.execute("SELECT COUNT(*) FROM pump_models")
if cursor.fetchone()[0] == 0:
    bombas_teste = [
        ("KSB",
         "MEGANORM-25-200",
         "209", 
         3500, 
         0.12, 
         18, 
         [1.6203366293119338e-05, -0.0006504262846409288, 0.007837100137631333, -0.10339741918416842, 0.11683996767802679, 94.15548733348413],
         [-0.0007761887470387009, 0.033911048199121115, -0.5576200263934282, 4.241235763784843, -15.590336323464351, 115.48640858022397],
         [-5.9633593936612955e-05, 0.003076816279138715, -0.059727118368036666, 0.5692279008187227, -2.4263270913352737, 4.095657732597875],
         [1.1285529591079345e-05, -0.00046960392949810037, 0.007490625515566242, -0.05418332751654858, 0.46983129211803865, 3.078216968283303]),
        ("KSB",
         "MEGANORM-25-200",
         "150",
         3500, 
         0.119, 
         11.226, 
         [-6.152875598437504e-06, -0.00023022196775162525, 0.005955038045778292, -0.07820630130773137, -0.021018516193400612, 25.40433865005285],
         [0.0005957057986353534, -0.007273210186231224, -0.019920490611375758, 0.49545611270670514, -2.0910020703194343, 27.418206810685476],
         [-0.001313160729249795, 0.04855998247365979, -0.6829280829365291, 4.632414138397304, -15.146400303100819, 19.964266391239043],
         [3.927710401118578e-05, -0.0008288170055392251, 0.007423227933962978, -0.0376179263242516, 0.24972081254062903, -1.7864415921948635])
    ]
    
    for bomba in bombas_teste:
        adicionar_bomba(*bomba)

print("Banco de dados criado com sucesso!")

# Fechar conexão
conn.close()
