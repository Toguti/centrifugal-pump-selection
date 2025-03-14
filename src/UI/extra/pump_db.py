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
        rotacao TEXT NOT NULL,
        vazao_min REAL NOT NULL,
        vazao_max REAL NOT NULL,
        coef_head TEXT NOT NULL,
        coef_eff TEXT NOT NULL,
        coef_npshr TEXT NOT NULL,
        coef_power TEXT NOT NULL,
        eff_bop REAL NOT NULL,
        eff_bop_flow REAL NOT NULL,
        p80_eff_bop_flow REAL NOT NULL,
        p110_eff_bop_flow REAL NOT NULL,       
        UNIQUE(marca, modelo, diametro, rotacao)
    )
""")

# Função para gerar coeficientes polinomiais aleatórios para teste


# Função para adicionar uma bomba ao banco de dados
def adicionar_bomba(marca, modelo, diametro, rotacao, vazao_min, vazao_max, coef_head, coef_eff, coef_npshr, coef_power, eff_bop, eff_bop_flow, p80_eff_bop_flow, p110_eff_bop_flow):
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
        INSERT INTO pump_models (marca, modelo, diametro, rotacao, vazao_min, vazao_max, coef_head, coef_eff, coef_npshr, coef_power, eff_bop, eff_bop_flow, p80_eff_bop_flow, p110_eff_bop_flow)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (marca, modelo, diametro, rotacao, vazao_min, vazao_max,
          coef_head_json, coef_eff_json, coef_npshr_json, coef_power_json,
           eff_bop, eff_bop_flow, p80_eff_bop_flow, p110_eff_bop_flow))
    
    conn.commit()
    print("Registro inserido com sucesso!")

print("Banco de dados criado com sucesso!")

# Fechar conexão
conn.close()
