CREATE NONCLUSTERED INDEX idx_alt_escolhida
ON atlas.alternativas (id_estudo, flag_alternativa_escolhida, id_alternativa DESC)
INCLUDE (
    dem_fp_ant,
    dem_p_ant,
    dem_fp_dep,
    dem_p_dep,
    etapa,
    custo_modular,
    ERD,
    demanda_disponivel_ponto,
    proporcionalidade,
    flag_menor_custo_global,
    flag_carga,
    flag_geracao
);

DROP INDEX idx_status_estudo_id_data ON atlas.status_estudo;
GO

CREATE NONCLUSTERED INDEX idx_status_estudo_id_data_desc
ON atlas.status_estudo (id_estudo, data DESC)
INCLUDE (id_status_tipo);


DROP INDEX idx_anexos_estudo ON atlas.anexos;
GO

CREATE NONCLUSTERED INDEX idx_anexos_estudo
ON atlas.anexos (id_estudo)
INCLUDE (id_anexo);

CREATE NONCLUSTERED INDEX idx_circuitos_id
ON atlas.circuitos (id_circuito)
INCLUDE (circuito, id_subestacao);

CREATE NONCLUSTERED INDEX idx_subestacoes_id
ON atlas.subestacoes (id_subestacao)
INCLUDE (nome, sigla, fronteira);
