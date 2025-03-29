import os
import re

def modify_csv_headers(input_file, output_file):
    """
    Modifica apenas os cabeçalhos do arquivo CSV para adicionar o número de estágios.
    Converte padrões como '000_headxflow' para '000_1_headxflow'.
    Também converte padrões como 'all_npshxflow' para 'all_1_npshxflow'.
    """
    # Lê o arquivo completo
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Modifica apenas a primeira linha (cabeçalho)
    header_line = lines[0].strip()
    headers = header_line.split(',')
    
    # Padrão para identificar cabeçalhos que precisam ser modificados
    # Inclui tanto padrões numéricos quanto 'all'
    pattern = re.compile(r'^(all|\d+)_(headxflow|effxflow|npshxflow|powerxflow)$')
    
    # Modifica os cabeçalhos
    modified_headers = []
    for header in headers:
        match = pattern.match(header.strip())
        if match:
            prefix = match.group(1)  # 'all' ou número do diâmetro
            curve_type = match.group(2)
            modified_header = f"{prefix}_1_{curve_type}"
            modified_headers.append(modified_header)
        else:
            modified_headers.append(header)
    
    # Escreve o arquivo de saída
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(','.join(modified_headers) + '\n')  # Cabeçalho modificado
        f.writelines(lines[1:])  # Restante do arquivo sem alterações

def process_directory(input_dir, output_dir):
    """
    Processa todos os arquivos CSV em um diretório.
    """
    # Cria o diretório de saída se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Lista todos os arquivos CSV no diretório de entrada
    csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    
    for csv_file in csv_files:
        input_path = os.path.join(input_dir, csv_file)
        output_path = os.path.join(output_dir, csv_file)
        
        print(f"Processando arquivo: {csv_file}")
        modify_csv_headers(input_path, output_path)
        print(f"Arquivo salvo em: {output_path}")

if __name__ == "__main__":
    # Diretório de entrada e saída para processar todos os arquivos
    input_dir = "src/db/pumps/raw_data"
    output_dir = "src/db/pumps/raw_data_modified"
    
    # Processa todos os arquivos CSV no diretório
    process_directory(input_dir, output_dir)
    
    print(f"Todos os arquivos CSV foram processados e salvos em: {output_dir}")