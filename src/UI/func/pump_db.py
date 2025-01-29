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
def gerar_polinomio_aleatorio():
    coef = np.random.uniform(-1, 1, 5)  # Gera coeficientes aleatórios para um polinômio de grau 4
    return json.dumps(coef.tolist())

# Função para adicionar uma bomba ao banco de dados
def adicionar_bomba(modelo, rotacao, vazao_min, vazao_max):
    coef_head = gerar_polinomio_aleatorio()
    coef_eff = gerar_polinomio_aleatorio()
    coef_npshr = gerar_polinomio_aleatorio()
    coef_power = gerar_polinomio_aleatorio()
    
    cursor.execute("""
        INSERT INTO bombas (modelo, rotacao, vazao_min, vazao_max, coef_head, coef_eff, coef_npshr, coef_power)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (modelo, rotacao, vazao_min, vazao_max, coef_head, coef_eff, coef_npshr, coef_power))
    
    conn.commit()

# Adicionar bombas fictícias se a tabela estiver vazia
cursor.execute("SELECT COUNT(*) FROM bombas")
if cursor.fetchone()[0] == 0:
    bombas_teste = [
        ("Bomba A", 3500, 5, 50),
        ("Bomba B", 2900, 3, 40),
        ("Bomba C", 1750, 10, 100)
    ]
    
    for bomba in bombas_teste:
        adicionar_bomba(*bomba)

print("Banco de dados criado com sucesso!")

# Fechar conexão
conn.close()
