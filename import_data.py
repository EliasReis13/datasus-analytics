import os
import pandas as pd
from sqlalchemy import create_engine, types # Alteração 1: Importado o 'types'

DB_USER = 'postgres'
DB_PASSWORD = '1234'  
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'dados_brutos_sus'

CSV_INPUT_PATH = "output_csv/"
TARGET_TABLE_NAME = 'dados_brutos_aih'

if __name__ == "__main__":
    try:
        connection_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        engine = create_engine(connection_string)
        print("Successfully connected to the PostgreSQL database.")
    except Exception as e:
        print(f"Error: Could not connect to the database. Please check your configuration. Details: {e}")
        exit()

    if not os.path.isdir(CSV_INPUT_PATH):
        print(f"Error: The input directory '{CSV_INPUT_PATH}' was not found.")
        exit()

    csv_files = [f for f in os.listdir(CSV_INPUT_PATH) if f.lower().endswith('.csv')]

    if not csv_files:
        print(f"No CSV files found in '{CSV_INPUT_PATH}'. Nothing to import.")
        exit()

    print(f"Found {len(csv_files)} CSV files to import into the '{TARGET_TABLE_NAME}' table.")

    for file_name in csv_files:
        file_path = os.path.join(CSV_INPUT_PATH, file_name)
        print(f"Processing '{file_name}'...")

        try:
            # Reads the CSV file. Adjust 'sep' and 'encoding' as necessary.
            df = pd.read_csv(file_path, sep=',', low_memory=False, encoding='utf-8')

            # Converts column names to lowercase for easier SQL querying.
            df.columns = df.columns.str.lower()

            # Alteração 2: Mapeia todas as colunas para o tipo VARCHAR (texto).
            # Isso previne erros de inferência de tipo de dados.
            dtype_mapping = {col: types.VARCHAR(length=255) for col in df.columns}

            # Anexa o conteúdo do DataFrame à tabela do banco de dados.
            df.to_sql(
                name=TARGET_TABLE_NAME,
                con=engine,
                if_exists='append',
                index=False,
                dtype=dtype_mapping  # Alteração 3: Aplica o mapeamento de tipos.
            )
            print(f"SUCCESS: Data from '{file_name}' was appended to the '{TARGET_TABLE_NAME}' table.")

        except Exception as e:
            print(f"ERROR: Failed to process '{file_name}'. Details: {e}")

    print("\nData import process finished.")