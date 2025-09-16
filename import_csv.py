import os
import csv
import psycopg2
import io

# --- SETTINGS ---
# Fill in with your PostgreSQL database credentials
DB_NAME = "datasus_bruto"
DB_USER = "postgres"
DB_PASS = "1234"  
DB_HOST = "localhost"          
DB_PORT = "5432"

# --- Automatic path configuration for the CSV folder ---
# This finds the absolute path of the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# This creates the full path to your CSV folder, relative to the script's location
CSV_FOLDER_PATH = os.path.join(script_dir, "BA_CSV")

def sanitize_name(name):
    """Sanitizes file and column names to be SQL-compliant."""
    # Remove the .csv extension and other problematic characters
    name = name.replace('.csv', '').replace('-', '_').replace(' ', '_').replace('.', '_')
    # Keep only alphanumeric characters and underscores
    return ''.join(c for c in name if c.isalnum() or c == '_')

def import_all_csvs():
    """Connects to the database and imports all CSVs from the configured folder."""
    conn = None
    try:
        # Connect to the database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Successfully connected to PostgreSQL!")

        # Iterate over all files in the folder
        for filename in os.listdir(CSV_FOLDER_PATH):
            if filename.endswith('.csv'):
                full_path = os.path.join(CSV_FOLDER_PATH, filename)
                table_name = sanitize_name(filename)

                with conn.cursor() as cursor:
                    # Read the CSV header to get column names (using latin-1)
                    with open(full_path, 'r', encoding='latin-1') as f:
                        reader = csv.reader(f, delimiter=',') 
                        headers = [sanitize_name(h) for h in next(reader)]

                    # Build the SQL command to create the table
                    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
                    create_table_sql += ", ".join([f'"{col}" TEXT' for col in headers])
                    create_table_sql += ");"
                    
                    print(f"\nCreating table '{table_name}'...")
                    cursor.execute(create_table_sql)

                    # Import the data using the COPY command (very fast)
                    print(f"Importing data from '{filename}' to '{table_name}'...")
                    
                    copy_sql = f"COPY {table_name} FROM STDIN WITH CSV HEADER DELIMITER ','"
                    with open(full_path, 'r', encoding='latin-1') as f:
                        # Read the raw content
                        raw_content = f.read()
                        # Remove the null bytes that cause the error
                        clean_content = raw_content.replace('\x00', '')
                        # Create an in-memory text stream with the clean content
                        string_io_file = io.StringIO(clean_content)
                        # Pass the clean stream to the copy_expert function
                        cursor.copy_expert(sql=copy_sql, file=string_io_file)

                    conn.commit()
                    print(f"File '{filename}' imported successfully!")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()
            print("\nPostgreSQL connection closed.")

if __name__ == "__main__":
    import_all_csvs()