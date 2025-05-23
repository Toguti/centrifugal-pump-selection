import sqlite3
import pandas as pd
import numpy as np
import os
import logging
import json

def create_database(db_path: str) -> None:
    """
    Cria o banco de dados e a tabela pump_models, se não existir.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pump_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            diametro TEXT NOT NULL,
            rotacao TEXT NOT NULL,
            estagios TEXT NOT NULL,
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
            UNIQUE(marca, modelo, diametro, rotacao, estagios)
        )
    """)
    conn.close()

def create_connection(db_path: str) -> sqlite3.Connection:
    """
    Cria e retorna uma conexão com o banco de dados SQLite.
    """
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

def inserir_bombas_em_lote(conn: sqlite3.Connection, registros: list) -> None:
    """
    Insere múltiplos registros de bombas no banco de dados utilizando INSERT OR IGNORE.
    
    A tabela possui restrição UNIQUE em (marca, modelo, diametro, rotacao, estagios),
    garantindo que registros duplicados sejam ignorados sem gerar exceção.
    
    Registra, via log, quantos registros foram inseridos e quantos foram ignorados.
    
    Parâmetros:
      conn      : Conexão ativa com o banco de dados.
      registros : Lista de tuplas contendo os registros a serem inseridos.
    """
    sql = """
    INSERT OR IGNORE INTO pump_models 
    (marca, modelo, diametro, rotacao, estagios, vazao_min, vazao_max, coef_head, coef_eff, coef_npshr, coef_power,
     eff_bop, eff_bop_flow, p80_eff_bop_flow, p110_eff_bop_flow)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    with conn:
        before_changes = conn.total_changes
        conn.executemany(sql, registros)
        after_changes = conn.total_changes

    inserted = after_changes - before_changes
    duplicates = len(registros) - inserted
    logging.info(f"{inserted} registros inseridos. {duplicates} registros duplicados ignorados.")

def transferir_csv_para_db(conn: sqlite3.Connection, caminho_csv: str, chunksize: int = None) -> None:
    """
    Lê um arquivo CSV utilizando pandas e insere os registros no banco de dados.
    
    Espera que o CSV possua as colunas:
      - 'Marca', 'Modelo', 'Diameter', 'Rotation', 'Stages', 'min_flow', 'max_flow',
      - 'flowxhead', 'flowxeff', 'flowxnpsh', 'flowxpower',
      - 'eff_bop', 'eff_bop_flow', 'p80_eff_bop_flow', 'p110_eff_bop_flow'
    """
    reader = pd.read_csv(caminho_csv, chunksize=chunksize) if chunksize else [pd.read_csv(caminho_csv)]
    
    for df in reader:
        # Normaliza os nomes das colunas removendo espaços
        df.columns = df.columns.str.strip()
        print(df)
        # Conversão de tipos para compatibilidade com o banco
        df['Diameter'] = df['Diameter'].astype(str)
        df['Rotation'] = df['Rotation'].astype(str)
        df['Stages'] = df['Stages'].astype(str)  # Nova coluna de estágios
        df['min_flow'] = df['min_flow'].astype(float)
        df['max_flow'] = df['max_flow'].astype(float)
        # Caso seja necessário, converta os coeficientes para string
        df['flowxhead'] = df['flowxhead'].astype(str)
        df['flowxeff'] = df['flowxeff'].astype(str)
        df['flowxnpsh'] = df['flowxnpsh'].astype(str)
        df['flowxpower'] = df['flowxpower'].astype(str)
        # Conversão das novas colunas para float
        df['eff_bop'] = df['eff_bop'].astype(float)
        df['eff_bop_flow'] = df['eff_bop_flow'].astype(float)
        df['p80_eff_bop_flow'] = df['p80_eff_bop_flow'].astype(float)
        df['p110_eff_bop_flow'] = df['p110_eff_bop_flow'].astype(float)

        # Seleção e ordenação das colunas conforme a estrutura da tabela
        registros = df[['Marca', 'Modelo', 'Diameter', 'Rotation', 'Stages', 'min_flow', 'max_flow', 
                        'flowxhead', 'flowxeff', 'flowxnpsh', 'flowxpower',
                        'eff_bop', 'eff_bop_flow', 'p80_eff_bop_flow', 'p110_eff_bop_flow']].to_records(index=False)
        
        registros = [tuple(reg) for reg in registros]
        inserir_bombas_em_lote(conn, registros)

if __name__ == "__main__":
    # Configuração básica de logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    # Definição dos caminhos para o banco de dados e os arquivos CSV
    DB_PATH = "src/db/pump_data.db"
    DATA_PATH = "src/db/pumps/processed_data"

    # Cria o Banco de Dados Caso não exista
    create_database(DB_PATH)
    
    # Cria a conexão com o banco e processa cada arquivo CSV encontrado na pasta
    with create_connection(DB_PATH) as conn:
        for file_name in os.listdir(DATA_PATH):
            if file_name.endswith(".csv"):
                caminho_completo = os.path.join(DATA_PATH, file_name)
                logging.info(f"Processando arquivo: {caminho_completo}")
                # Para arquivos grandes, defina um chunksize apropriado (ex.: 10000)
                transferir_csv_para_db(conn, caminho_completo, chunksize=10000)
    
    logging.info("Processamento concluído.")