import os
import pandas as pd
from simpledbf import Dbf5

# --- Configuration ---

DBF_INPUT_PATH = "input_dbf/"
CSV_OUTPUT_PATH = "output_csv/"

def dbf_to_csv(dbf_file_path, output_path, file_name, original_filename):
    """
    Converts a single DBF file to a CSV file using simpledbf and pandas libraries.
    """
    # Ensure the output directory exists
    os.makedirs(output_path, exist_ok=True)

    output_file = os.path.join(output_path, file_name + ".csv")

    try:
        # Load the DBF file, specifying the 'latin1' codec.
        # NOTE: Kept the context about Brazilian data as it's very important.
        # This is a common source of errors for data from Brazil.
        dbf = Dbf5(dbf_file_path, codec='latin1')

        # Convert to a pandas DataFrame
        df = dbf.to_dataframe()

        # Save the DataFrame as a CSV file using UTF-8 encoding
        df.to_csv(output_file, index=False, encoding='utf-8')

        # IMPROVEMENT: Using the 'original_filename' variable (like 'file.dbf') 
        # makes the log message more accurate than hardcoding '.dbc'.
        print(f"SUCCESS: File '{original_filename}' was converted to '{file_name}.csv'")
        return True

    except Exception as e:
        print(f"ERROR: An unexpected error occurred while processing '{original_filename}': {e}")
        return False

# --- Main Logic ---
if __name__ == "__main__":
    # Ensure the input directory exists before starting
    if not os.path.isdir(DBF_INPUT_PATH):
        print(f"Error: The input directory '{DBF_INPUT_PATH}' was not found.")
    else:
        # To avoid re-processing files, create a list of already converted CSVs.
        # This checks the output folder for existing .csv files and extracts their base names.
        try:
            # It's safer to check if the output path exists before listing its files
            if not os.path.exists(CSV_OUTPUT_PATH):
                os.makedirs(CSV_OUTPUT_PATH)
            
            already_converted = [f.split(".")[0] for f in os.listdir(CSV_OUTPUT_PATH) if f.lower().endswith('.csv')]
        except FileNotFoundError:
            already_converted = []

        print("Starting conversion...")
        for filename in os.listdir(DBF_INPUT_PATH):
            # Process only files with .dbc or .dbf extensions (case-insensitive)
            if filename.lower().endswith(('.dbc', '.dbf')):
                
                base_name = os.path.splitext(filename)[0]

                if base_name not in already_converted:
                    print(f"Processing file: {filename}")
                    dbf_full_path = os.path.join(DBF_INPUT_PATH, filename)
                    # Pass the original filename to the function for better logging
                    dbf_to_csv(dbf_full_path, CSV_OUTPUT_PATH, base_name, filename)
                else:
                    print(f"File '{filename}' seems to be already converted. Skipping.")
        
        print("Conversion process finished.")