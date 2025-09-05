import os
import csv
from dbfread import DBF

dbf_files_path = "ciha_dbf/"
csv_output_path = "ciha_csv/"

def dbf_to_csv(dbf_file, output_path, file_name):
    dbf = DBF(dbf_file)
    with open(output_path + file_name + ".csv", 'w', newline = '') as f:
        writer = csv.writer(f)
        writer.writerow(dbf.field_names)
        for record in dbf:
            writer.writerow(list(record.values()))
    return True

done = [x.split(".")[0] for x in os.listdir(csv_output_path)]

for f in os.listdir(dbf_files_path):
    file_name = f.split(".")[0]
    if file_name not in done:
        print(f)
        dbf_to_csv(dbf_files_path + f, csv_output_path, file_name)     