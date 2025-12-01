-- =============================================================================
-- SIHSUS Data Warehouse - Populate Dimensions
-- Description: Extract unique values from staging area, clean, and load.
-- =============================================================================

-- 1. Populate Dim_Localizacao
-- Rule: Filtering only Bahia (BA) based on project scope.
INSERT INTO dw.Dim_Localizacao (codigo_ibge, nome_municipio, uf)
SELECT DISTINCT
    codigo_ibge,
    nome,
    'BA' -- Hardcoded 'BA' since source was pre-filtered
FROM
    public.dados_brutos_municipios;

-- 2. Populate Dim_Estabelecimento
-- Rule: Links to Location ID (Snowflake).
INSERT INTO dw.Dim_Estabelecimento (cnes, id_localizacao)
SELECT DISTINCT
    cnes_bruto.cnes,
    loc.id_localizacao
FROM
    public.dados_brutos_cnes AS cnes_bruto
LEFT JOIN
    dw.Dim_Localizacao AS loc ON cnes_bruto.codufmun = loc.codigo_ibge;

-- 3. Populate Dim_Procedimento
-- Step A: Insert official data
INSERT INTO dw.Dim_Procedimento (cod_procedimento, nome_procedimento)
SELECT DISTINCT codproc, nome FROM public.dados_brutos_procedimentos;

-- Step B: Handle "Orphan" records (Procedures in AIH but not in official list)
-- Prevents Foreign Key violation errors
INSERT INTO dw.Dim_Procedimento (cod_procedimento, nome_procedimento)
SELECT DISTINCT aih.proc_rea, 'PROCEDIMENTO NÃO IDENTIFICADO NA BASE OFICIAL'
FROM public.dados_brutos_aih AS aih
WHERE NOT EXISTS (SELECT 1 FROM dw.Dim_Procedimento AS p WHERE p.cod_procedimento = aih.proc_rea);

-- 4. Populate Dim_CID
-- Step A: Insert official data (Cleaning spaces and standardizing casing)
INSERT INTO dw.Dim_CID (cod_cid, nome_cid)
SELECT DISTINCT TRIM(UPPER(codigo)), descricao FROM public.dados_brutos_cid;

-- Step B: Handle "Orphan" records
INSERT INTO dw.Dim_CID (cod_cid, nome_cid)
SELECT DISTINCT aih.diag_princ, 'CID NÃO IDENTIFICADO NA BASE OFICIAL'
FROM public.dados_brutos_aih AS aih
WHERE NOT EXISTS (SELECT 1 FROM dw.Dim_CID AS c WHERE c.cod_cid = aih.diag_princ);

-- 5. Populate Dim_Pessoa
-- Rule: Standardize Race/Color codes ('1' vs '01') and Age Units.
-- Filter: Only records from 2019 onwards.
INSERT INTO dw.Dim_Pessoa (idade, unidade_idade, sexo, raca_cor, morte)
SELECT DISTINCT
    aih.idade::INTEGER,
    -- Age Unit Normalization
    CASE aih.cod_idade 
        WHEN '4' THEN 'Anos' 
        WHEN '3' THEN 'Meses' 
        WHEN '2' THEN 'Dias' 
        WHEN '1' THEN 'Horas' 
        ELSE 'Não informado' 
    END,
    -- Sex Normalization
    CASE aih.sexo 
        WHEN '1' THEN 'Masculino' 
        WHEN '3' THEN 'Feminino' 
        ELSE 'Ignorado' 
    END,
    -- Race/Color Cleaning and Standardization
    CASE TRIM(aih.raca_cor)
        WHEN '01' THEN 'Branca'     WHEN '1' THEN 'Branca'
        WHEN '02' THEN 'Preta'      WHEN '2' THEN 'Preta'
        WHEN '03' THEN 'Parda'      WHEN '3' THEN 'Parda'
        WHEN '04' THEN 'Amarela'    WHEN '4' THEN 'Amarela'
        WHEN '05' THEN 'Indígena'   WHEN '5' THEN 'Indígena'
        WHEN '99' THEN 'Sem Informação'
        ELSE 'Ignorado/Não Preenchido'
    END,
    -- Death Boolean
    CASE aih.morte WHEN '1' THEN TRUE ELSE FALSE END
FROM
    public.dados_brutos_aih AS aih
WHERE
    aih.ano_cmpt::INTEGER >= 2019;