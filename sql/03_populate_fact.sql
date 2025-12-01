-- =============================================================================
-- SIHSUS Data Warehouse - Populate Fact Table
-- Description: Loads Fact_Internacoes with metrics and lookup keys.
-- =============================================================================

INSERT INTO dw.Fato_Internacoes (
    id_pessoa, 
    cnes, 
    cod_procedimento_realizado, 
    cod_cid_principal,
    ano, 
    mes,
    valor_total_pago, 
    valor_servicos_hospitalares, 
    valor_servicos_profissionais, 
    valor_uti, 
    dias_permanencia
)
SELECT
    -- 1. Dimension Keys (Lookups)
    p.id_pessoa,
    aih.cnes,
    aih.proc_rea,
    aih.diag_princ,

    -- 2. Degenerate Dimension (Time)
    aih.ano_cmpt::INTEGER,
    aih.mes_cmpt::INTEGER,

    -- 3. Metrics (Casting text to numeric)
    aih.val_tot::NUMERIC,
    aih.val_sh::NUMERIC,
    aih.val_sp::NUMERIC,
    aih.val_uti::NUMERIC,
    aih.dias_perm::INTEGER

FROM
    public.dados_brutos_aih AS aih

-- 4. Joins to resolve Surrogate Keys (IDs)
-- Complex Join with Dim_Pessoa to match the generated ID based on attributes
LEFT JOIN dw.Dim_Pessoa AS p ON
    aih.idade::INTEGER = p.idade
    AND CASE aih.cod_idade WHEN '4' THEN 'Anos' WHEN '3' THEN 'Meses' WHEN '2' THEN 'Dias' WHEN '1' THEN 'Horas' ELSE 'Não informado' END = p.unidade_idade
    AND CASE aih.sexo WHEN '1' THEN 'Masculino' WHEN '3' THEN 'Feminino' ELSE 'Ignorado' END = p.sexo
    AND CASE TRIM(aih.raca_cor) WHEN '01' THEN 'Branca' WHEN '1' THEN 'Branca' WHEN '02' THEN 'Preta' WHEN '2' THEN 'Preta' WHEN '03' THEN 'Parda' WHEN '3' THEN 'Parda' WHEN '04' THEN 'Amarela' WHEN '4' THEN 'Amarela' WHEN '05' THEN 'Indígena' WHEN '5' THEN 'Indígena' WHEN '99' THEN 'Sem Informação' ELSE 'Ignorado/Não Preenchido' END = p.raca_cor
    AND CASE aih.morte WHEN '1' THEN TRUE ELSE FALSE END = p.morte

-- 5. Filter (Scope)
WHERE
    aih.ano_cmpt::INTEGER >= 2019;