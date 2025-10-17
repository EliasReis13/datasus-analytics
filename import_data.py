import os
import pandas as pd
from sqlalchemy import create_engine, types

DB_USER = 'postgres'
DB_PASSWORD = '1234'  
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'dados_brutos_sus'

# Define os caminhos e nomes das tabelas
AIH_INPUT_PATH = "output_csv/"
PROC_INPUT_FILE = "input_lookup/procedimento.csv"
CID_INPUT_FILE = "input_lookup/cid.csv"
CNES_INPUT_PATH = "cnes_csv/"
MUN_INPUT_FILE = "input_lookup/municipios_bahia.csv"

TARGET_TABLE_AIH = "dados_brutos_aih"
TARGET_TABLE_PROC = "dados_brutos_procedimentos"
TARGET_TABLE_CID = "dados_brutos_cid"
TARGET_TABLE_CNES = "dados_brutos_cnes"
TARGET_TABLE_MUN = "dados_brutos_municipios"

if __name__ == "__main__":
    try:
        connection_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        engine = create_engine(connection_string)
        print("Successfully connected to the PostgreSQL database.\n")
    except Exception as e:
        print(f"Error: Could not connect to the database. Details: {e}")
        exit()

    # --- TAREFA 1: Importar Dados de Internação (AIH) ---
    print("--- Starting Task 1: Hospitalizations (AIH) ---")
    if os.path.isdir(AIH_INPUT_PATH):
        csv_files = [f for f in os.listdir(AIH_INPUT_PATH) if f.lower().endswith('.csv')]
        print(f"Found {len(csv_files)} AIH files to import.")
        for file_name in csv_files:
            file_path = os.path.join(AIH_INPUT_PATH, file_name)
            try:
                df = pd.read_csv(file_path, sep=',', low_memory=False, encoding='utf-8')
                df.columns = df.columns.str.lower()
                dtype_mapping = {col: types.VARCHAR(length=255) for col in df.columns}
                df.to_sql(name=TARGET_TABLE_AIH, con=engine, if_exists='append', index=False, dtype=dtype_mapping)
                print(f"SUCCESS: Appended '{file_name}' to '{TARGET_TABLE_AIH}'.")
            except Exception as e:
                print(f"ERROR processing '{file_name}': {e}")
    else:
        print(f"Warning: Directory '{AIH_INPUT_PATH}' not found. Skipping AIH import.")
    print("--- Finished Task 1 ---\n")
    
    # --- TAREFA 2: Importar Dados de Procedimentos ---
    print("--- Starting Task 2: Procedures ---")
    if os.path.isfile(PROC_INPUT_FILE):
        try:
            df_proc = pd.read_csv(PROC_INPUT_FILE, sep=';', low_memory=False, encoding='utf-8')
            df_proc.columns = df_proc.columns.str.lower()
            dtype_mapping = {col: types.VARCHAR(length=255) for col in df_proc.columns}
            df_proc.to_sql(name=TARGET_TABLE_PROC, con=engine, if_exists='replace', index=False, dtype=dtype_mapping)
            print(f"SUCCESS: Loaded '{PROC_INPUT_FILE}' into '{TARGET_TABLE_PROC}'. Table was replaced.")
        except Exception as e:
            print(f"ERROR processing '{PROC_INPUT_FILE}': {e}")
    else:
        print(f"Warning: File '{PROC_INPUT_FILE}' not found. Skipping Procedure import.")
    print("--- Finished Task 2 ---\n")

    # --- TAREFA 3: Importar Dados de CID ---
    print("--- Starting Task 3: CIDs ---")
    if os.path.isfile(CID_INPUT_FILE):
        try:
            df_cid = pd.read_csv(CID_INPUT_FILE, sep=';', low_memory=False, encoding='utf-8')
            df_cid.columns = df_cid.columns.str.lower()
            dtype_mapping = {col: types.TEXT for col in df_cid.columns}
            df_cid.to_sql(name=TARGET_TABLE_CID, con=engine, if_exists='replace', index=False, dtype=dtype_mapping)
            print(f"SUCCESS: Loaded '{CID_INPUT_FILE}' into '{TARGET_TABLE_CID}'. Table was replaced.")
        except Exception as e:
            print(f"ERROR processing '{CID_INPUT_FILE}': {e}")
    else:
        print(f"Warning: File '{CID_INPUT_FILE}' not found. Skipping CID import.")
    print("--- Finished Task 3 ---\n")

    # --- TAREFA 4: Importar Dados de Estabelecimentos (CNES) ---
    print("--- Starting Task 4: CNES Establishments ---")
    if os.path.isdir(CNES_INPUT_PATH):
        cnes_files = [f for f in os.listdir(CNES_INPUT_PATH) if f.lower().endswith('.csv')]
        print(f"Found {len(cnes_files)} CNES files to process.")
        
        # Lista para guardar todos os DataFrames lidos
        list_of_dfs = []
        for file_name in cnes_files:
            file_path = os.path.join(CNES_INPUT_PATH, file_name)
            print(f"Reading '{file_name}' into memory...")
            try:
                # Lê cada arquivo e adiciona à lista
                df_cnes = pd.read_csv(file_path, sep=',', low_memory=False, encoding='latin1', quotechar='"')
                list_of_dfs.append(df_cnes)
            except Exception as e:
                print(f"ERROR reading '{file_name}': {e}")
        
        if list_of_dfs:
            try:
                # Concatena todos os DataFrames da lista em um só
                print("\nConcatenating all CNES files... This may take a moment.")
                master_df = pd.concat(list_of_dfs, ignore_index=True)
                
                print(f"Concatenation complete. Total rows: {len(master_df)}")
                
                master_df.columns = master_df.columns.str.lower()
                dtype_mapping = {col: types.VARCHAR(length=255) for col in master_df.columns}

                print(f"Loading all {len(master_df)} rows into '{TARGET_TABLE_CNES}'...")
                # Usa 'replace' para garantir uma carga limpa e 'chunksize' para eficiência
                master_df.to_sql(
                    name=TARGET_TABLE_CNES, 
                    con=engine, 
                    if_exists='replace', 
                    index=False, 
                    dtype=dtype_mapping,
                    chunksize=10000  # Carrega em lotes de 10000 linhas para economizar memória
                )
                print(f"SUCCESS: All CNES data loaded into '{TARGET_TABLE_CNES}'.")
            except Exception as e:
                print(f"ERROR during concatenation or database load: {e}")
    else:
        print(f"Warning: Directory '{CNES_INPUT_PATH}' not found. Skipping CNES import.")
    print("--- Finished Task 4 ---\n")

    print("--- Starting Task 5: Municipalities ---")
    if os.path.isfile(MUN_INPUT_FILE):
        try:
            # O separador aqui é vírgula ',', conforme o arquivo original do IBGE
            df_mun = pd.read_csv(MUN_INPUT_FILE, sep=',', low_memory=False, encoding='utf-8')
            df_mun.columns = df_mun.columns.str.lower()
            dtype_mapping = {col: types.VARCHAR(length=255) for col in df_mun.columns}
            
            # Usamos 'replace' para garantir que a tabela esteja sempre atualizada
            df_mun.to_sql(name=TARGET_TABLE_MUN, con=engine, if_exists='replace', index=False, dtype=dtype_mapping)
            print(f"SUCCESS: Loaded '{MUN_INPUT_FILE}' into '{TARGET_TABLE_MUN}'. Table was replaced.")
        except Exception as e:
            print(f"ERROR processing '{MUN_INPUT_FILE}': {e}")
    else:
        print(f"Warning: File '{MUN_INPUT_FILE}' not found. Skipping Municipality import.")
    print("--- Finished Task 5 ---\n")

    print("All import tasks finished.")