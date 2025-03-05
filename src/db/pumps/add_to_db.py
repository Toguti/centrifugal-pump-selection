import sqlite3
import pandas as pd
import os
import logging

def create_connection(db_path: str) -> sqlite3.Connection:
    """
    Cria e retorna uma conexão com o banco de dados SQLite.

    Otimizações:
      - Configura o journal_mode para WAL e synchronous para NORMAL,
        melhorando a performance em inserções em massa.
    """
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

def inserir_bombas_em_lote(conn: sqlite3.Connection, registros: list) -> None:
    """
    Insere múltiplos registros de bombas no banco de dados utilizando INSERT OR IGNORE.
    
    A tabela já possui a restrição UNIQUE em (marca, modelo, diametro, rotacao),
    garantindo que registros duplicados sejam ignorados sem gerar exceção.
    
    Parâmetros:
      conn      : Conexão ativa com o banco de dados.
      registros : Lista de tuplas contendo os registros a serem inseridos.
    """
    sql = """
    INSERT OR IGNORE INTO pump_models 
    (marca, modelo, diametro, rotacao, vazao_min, vazao_max, coef_head, coef_eff, coef_npshr, coef_power)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    with conn:
        conn.executemany(sql, registros)
    logging.info(f"{len(registros)} registros processados para inserção (duplicatas ignoradas).")

def transferir_csv_para_db(conn: sqlite3.Connection, caminho_csv: str, chunksize: int = None) -> None:
    """
    Lê um arquivo CSV utilizando pandas e insere os registros no banco de dados.
    
    O CSV deve conter o cabeçalho:
      Marca,Modelo,Diameter,Rotation,min_flow,max_flow,flowxhead,flowxeff,flowxnpsh,flowxpower
    
    Conversões realizadas:
      - 'Diameter' é convertido para string.
      - 'Rotation' para inteiro.
      - 'min_flow' e 'max_flow' para float.
      - Os coeficientes permanecem como string.
    
    Parâmetros:
      conn      : Conexão ativa com o banco.
      caminho_csv : Caminho para o arquivo CSV.
      chunksize   : (Opcional) Número de linhas por chunk para leitura. Útil para arquivos grandes.
    """
    # Se chunksize for especificado, utiliza leitura em blocos; caso contrário, lê o arquivo inteiro.
    reader = pd.read_csv(caminho_csv, chunksize=chunksize) if chunksize else [pd.read_csv(caminho_csv)]
    
    for df in reader:
        # Ajusta os tipos de dados conforme o padrão do banco de dados
        df['Diameter'] = df['Diameter'].astype(str)
        df['Rotation'] = df['Rotation'].astype(int)
        df['min_flow'] = df['min_flow'].astype(float)
        df['max_flow'] = df['max_flow'].astype(float)
        
        # Converte o DataFrame para uma lista de tuplas na ordem correta
        registros = df[['Marca', 'Modelo', 'Diameter', 'Rotation', 'min_flow', 'max_flow', 
                        'flowxhead', 'flowxeff', 'flowxnpsh', 'flowxpower']].to_records(index=False)
        registros = [tuple(reg) for reg in registros]
        
        inserir_bombas_em_lote(conn, registros) 

if __name__ == "__main__":
    # Configuração básica de logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    # Definição dos caminhos para o banco de dados e os arquivos CSV
    db_path = "src/db/pump_data.db"
    data_path = "src/db/pumps/processed_data"
    
    # Cria a conexão com o banco e processa cada arquivo CSV encontrado na pasta
    with create_connection(db_path) as conn:
        for file_name in os.listdir(data_path):
            if file_name.endswith(".csv"):
                caminho_completo = os.path.join(data_path, file_name)
                logging.info(f"Processando arquivo: {caminho_completo}")
                # Para arquivos grandes, defina um chunksize apropriado (ex.: 10000)
                transferir_csv_para_db(conn, caminho_completo, chunksize=10000)
    
    logging.info("Processamento concluído.")
