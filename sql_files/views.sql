CREATE VIEW gciweb.vw_estudos_completos AS
SELECT
    e.id_estudo,
    e.num_doc,
    e.protocolo,
    e.nome_projeto,
    e.descricao,
    e.instalacao,
    e.n_alternativas,
    e.latitude_cliente,
    e.longitude_cliente,
    e.observacao,
    edp.empresa,
    r.regional,
    u_criador.nome AS nome_criador,
    u_resp.nome AS nome_responsavel,
    emp.nome_empresa,
    m.municipio,
    e.data_registro,
    ts.viabilidade,
    ts.analise,
    ts.pedido,
    e.data_abertura_cliente,
    e.data_desejada_cliente,
    e.data_vencimento_cliente,
    e.data_prevista_conexao,
    e.data_vencimento_ddpe,
    e.dem_carga_atual_fp,
    e.dem_carga_atual_p,
    e.dem_carga_solicit_fp,
    e.dem_carga_solicit_p,
    e.dem_ger_atual_fp,
    e.dem_ger_atual_p,
    e.dem_ger_solicit_fp,
    e.dem_ger_solicit_p,
    t.tensao,
    e.data_alteracao,

    /* ? Quantidade de Anexos */
    anexos.qtd_anexos,

    /* ? Último Status */
    ultimo_status.status AS ultimo_status,

    /* ? Alternativa Escolhida */
    alt_escolhida.id_alternativa,
    alt_escolhida.descricao AS alternativa_descricao,
    alt_escolhida.dem_fp_ant AS alternativa_dem_fp_ant,
    alt_escolhida.dem_p_ant AS alternativa_dem_p_ant,
    alt_escolhida.circuito AS alternativa_circuito,
	alt_escolhida.nome AS subestacao,
	alt_escolhida.sigla as sigla_subestacao,
	alt_escolhida.fronteira as fronteira,
	alt_escolhida.custo_modular as custo_modular,

	alt_escolhida.subgrupo_tarifario,
	alt_escolhida.etapa,
	alt_escolhida.dem_fp_dep,
	alt_escolhida.dem_p_dep,
	alt_escolhida.ERD,
	alt_escolhida.demanda_disponivel_ponto,
	alt_escolhida.proporcionalidade,
	alt_escolhida.flag_alternativa_escolhida,
	alt_escolhida.flag_menor_custo_global,
	alt_escolhida.flag_carga,
	alt_escolhida.flag_geracao,
	alt_escolhida.observacao as alternativa_observacao

FROM gciweb.estudos e
LEFT JOIN gciweb.edp edp ON e.id_edp = edp.id_edp
LEFT JOIN gciweb.regionais r ON e.id_regional = r.id_regional
LEFT JOIN gciweb.usuarios u_criador ON e.id_criado_por = u_criador.id_usuario
LEFT JOIN gciweb.resp_regioes rr ON e.id_resp_regiao = rr.id_resp_regiao
LEFT JOIN gciweb.usuarios u_resp ON rr.id_usuario = u_resp.id_usuario
LEFT JOIN gciweb.empresas emp ON e.id_empresa = emp.id_empresa
LEFT JOIN gciweb.municipios m ON e.id_municipio = m.id_municipio
LEFT JOIN gciweb.tipo_solicitacao ts ON e.id_tipo_solicitacao = ts.id_tipo_solicitacao
LEFT JOIN gciweb.tensao t ON e.id_tensao = t.id_tensao

/* =======================================================
   ? CROSS APPLY — Alternativa Escolhida
   ======================================================= */
OUTER APPLY (
    SELECT TOP 1
        alt.id_alternativa,
        alt.descricao,
		alt.subgrupo_tarifario,
		alt.etapa,
        alt.dem_fp_ant,
        alt.dem_p_ant,
		alt.dem_fp_dep,
		alt.dem_p_dep,
		alt.custo_modular,
		alt.ERD,
		alt.demanda_disponivel_ponto,
		alt.proporcionalidade,
		alt.flag_alternativa_escolhida,
		alt.flag_menor_custo_global,
		alt.flag_carga,
		alt.flag_geracao,
		alt.observacao,
        circ.circuito,
		sbt.nome,
		sbt.sigla,
		sbt.fronteira
    FROM gciweb.alternativas alt
    LEFT JOIN gciweb.circuitos circ ON circ.id_circuito = alt.id_circuito
	LEFT JOIN gciweb.subestacoes sbt ON sbt.id_subestacao = circ.id_subestacao
    WHERE alt.id_estudo = e.id_estudo
      AND alt.flag_alternativa_escolhida = 1
    ORDER BY alt.id_alternativa DESC
) alt_escolhida

/* =======================================================
   ? CROSS APPLY — Último Status
   ======================================================= */
OUTER APPLY (
    SELECT TOP 1
        st.status
    FROM gciweb.status_estudo se
    LEFT JOIN gciweb.status_tipos st
        ON st.id_status_tipo = se.id_status_tipo
    WHERE se.id_estudo = e.id_estudo
    ORDER BY se.data DESC
) ultimo_status

/* =======================================================
   ? CROSS APPLY — Contagem de Anexos
   ======================================================= */
OUTER APPLY (
    SELECT COUNT(*) AS qtd_anexos
    FROM gciweb.anexos a
    WHERE a.id_estudo = e.id_estudo
) anexos;
