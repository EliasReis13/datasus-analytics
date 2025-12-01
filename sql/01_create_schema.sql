-- =============================================================================
-- SIHSUS Data Warehouse - Schema Creation
-- Description: Defines the dimensional model (Star/Snowflake Schema).
-- =============================================================================

-- 1. Setup Environment
DROP SCHEMA IF EXISTS dw CASCADE;
CREATE SCHEMA dw;

-- =============================================================================
-- 2. Create Dimension Tables
-- =============================================================================

-- Dimension: Location (Geography)
CREATE TABLE dw.Dim_Localizacao (
    id_localizacao SERIAL PRIMARY KEY,
    codigo_ibge VARCHAR(7) NOT NULL UNIQUE,
    nome_municipio VARCHAR(255) NOT NULL,
    uf CHAR(2) NOT NULL
);

-- Dimension: Establishment (Hospitals/Clinics)
CREATE TABLE dw.Dim_Estabelecimento (
    cnes VARCHAR(15) PRIMARY KEY, -- Business Key used as PK
    id_localizacao INT REFERENCES dw.Dim_Localizacao(id_localizacao)
);

-- Dimension: Procedure (Medical Procedures)
CREATE TABLE dw.Dim_Procedimento (
    cod_procedimento VARCHAR(10) PRIMARY KEY,
    nome_procedimento TEXT
);

-- Dimension: CID (Diseases/Diagnosis)
CREATE TABLE dw.Dim_CID (
    cod_cid VARCHAR(10) PRIMARY KEY,
    nome_cid TEXT
);

-- Dimension: Person (Patient Profile)
CREATE TABLE dw.Dim_Pessoa (
    id_pessoa SERIAL PRIMARY KEY,
    idade INT,
    unidade_idade VARCHAR(50),
    sexo VARCHAR(20),
    raca_cor VARCHAR(50),
    morte BOOLEAN
);

-- =============================================================================
-- 3. Create Fact Table
-- =============================================================================

-- Fact Table: Hospitalizations
CREATE TABLE dw.Fato_Internacoes (
    -- Foreign Keys (Dimensions)
    id_pessoa INT REFERENCES dw.Dim_Pessoa(id_pessoa),
    cnes VARCHAR(15) REFERENCES dw.Dim_Estabelecimento(cnes),
    cod_procedimento_realizado VARCHAR(10) REFERENCES dw.Dim_Procedimento(cod_procedimento),
    cod_cid_principal VARCHAR(10) REFERENCES dw.Dim_CID(cod_cid),

    -- Degenerate Dimension (Time)
    ano INT NOT NULL,
    mes INT NOT NULL,

    -- Measures (Metrics)
    quantidade_aih INT DEFAULT 1,
    valor_total_pago NUMERIC(15, 2),
    valor_servicos_hospitalares NUMERIC(15, 2),
    valor_servicos_profissionais NUMERIC(15, 2),
    valor_uti NUMERIC(15, 2),
    dias_permanencia INT
);