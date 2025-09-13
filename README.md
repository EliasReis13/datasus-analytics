# DATASUS Hospitalization Analysis (BI Project)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A project to extract, transform, and analyze public hospitalization data (AIH/SIHSUS) from the Brazilian Health System (DATASUS). 

---

## 1. Setup

This project uses **Python**. First, create a virtual environment and install the dependencies from the `requirements.txt` file.

### On Windows

```script
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```
### On macOS and Linux
```script
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### Step 1: Download Raw Data

- **Website:** [DATASUS File Transfer Portal](https://datasus.saude.gov.br/transferencia-de-arquivos)  
- **System:** SIHSUS (Hospital Information Systems)  

**Data Scope:**
- **UF:** Bahia (BA)  
- **Years:** 2019, 2020, 2021, 2022, 2023, and 2024  
- **Months:** January to December for each year  

---

### Step 2: Decompress `.DBC` to `.DBF`

The downloaded `.dbc` files must be decompressed to `.dbf`.  

Use the **TABWIN software**:  
`Arquivo -> Comprime/Expande.DBF` (as specified in the project guide).  

Place all resulting `.dbf` files into the `input_dbf/` directory.  

---

### Step 3: Convert `.DBF` to `.CSV`

This step uses the project's Python script to convert all `.dbf` files to `.csv`.  

Make sure all `.dbf` files are in the `input_dbf/` folder and run:

```script
python convert_dbf_to_csv.py
```