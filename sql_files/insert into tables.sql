--insert into gciweb.edp (empresa) values ('SP')
--insert into gciweb.edp (empresa) values ('ES')

insert into gciweb.FATOR_K(k, kg, subgrupo_tarif, data_ref, id_edp) values (269.39, 192.79, 'A4', '2024-10-22', 1)
insert into gciweb.FATOR_K(k, kg, subgrupo_tarif, data_ref, id_edp) values (269.39, 192.79, 'A3a', '2024-10-22', 1)
insert into gciweb.FATOR_K(k, subgrupo_tarif, data_ref, id_edp) values (48.38,'A2', '2024-10-22', 1)
insert into gciweb.FATOR_K(k, kg, subgrupo_tarif, data_ref, id_edp) values (1334.44, 722.58, 'A4', '2024-08-06', 2)
insert into gciweb.FATOR_K(k, kg, subgrupo_tarif, data_ref, id_edp) values (1334.44, 722.58, 'A3a', '2024-08-06', 2)
insert into gciweb.FATOR_K(k, kg, subgrupo_tarif, data_ref, id_edp) values (392.87, 263.54, 'A3', '2024-08-06', 2)
insert into gciweb.FATOR_K(k, subgrupo_tarif, data_ref, id_edp) values (60.07,'A2', '2024-08-06', 2)
insert into gciweb.FATOR_K(k, kg, subgrupo_tarif, data_ref, id_edp) values (1363.70, 669.45, 'A4', '2025-08-06', 2)
insert into gciweb.FATOR_K(k, kg, subgrupo_tarif, data_ref, id_edp) values (1363.70, 669.45, 'A3a', '2025-08-06', 2)
insert into gciweb.FATOR_K(k, kg, subgrupo_tarif, data_ref, id_edp) values (412.24, 286.98, 'A3', '2025-08-06', 2)
insert into gciweb.FATOR_K(k, kg, subgrupo_tarif, data_ref, id_edp) values (67.34, 168.81,'A2', '2025-08-06', 2)


insert into gciweb.municipios(municipio, id_edp) values ('Guarulhos', 1)
insert into gciweb.municipios(municipio, id_edp) values ('Cachoeira Paulista', 1)
insert into gciweb.municipios(municipio, id_edp) values ('Vitoria', 2);

Go

insert into gciweb.tipo_solicitacao(viabilidade, analise, pedido) values ('Orçamento Estimado', 'Carga', 'Ligação Nova')
insert into gciweb.tipo_solicitacao(viabilidade, analise, pedido) values ('Orçamento Estimado', 'MMGD', 'Aumento de Demanda')
insert into gciweb.tipo_solicitacao(viabilidade, analise, pedido) values ('Orçamento Estimado', 'MMGD', 'Ligação Nova')
insert into gciweb.tipo_solicitacao(viabilidade, analise, pedido) values ('Orçamento de Conexão', 'Carga', 'Ligação Nova')
insert into gciweb.tipo_solicitacao(viabilidade, analise, pedido) values ('Orçamento de Conexão', 'Carga', 'Aumento de Demanda')
insert into gciweb.tipo_solicitacao(viabilidade, analise, pedido) values ('Orçamento de Conexão', 'MMGD', 'Aumento de Demanda')
insert into gciweb.tipo_solicitacao(viabilidade, analise, pedido) values ('Orçamento de Conexão', 'MMGD', 'Ligação Nova')
insert into gciweb.tipo_solicitacao(viabilidade, analise, pedido) values ('Anteprojeto', 'Subestação', 'Ligação Nova')
insert into gciweb.tipo_solicitacao(viabilidade, analise, pedido) values ('Anteprojeto', 'Linhas', 'Ligação Nova')
insert into gciweb.tipo_solicitacao(viabilidade, analise, pedido) values ('Anteprojeto', 'Redes', 'Ligação Nova')
insert into gciweb.tipo_solicitacao(viabilidade, analise, pedido) values ('Outros', 'ONS', 'Carta')
insert into gciweb.tipo_solicitacao(viabilidade, analise, pedido) values ('Outros', 'ANEEL', 'Carta')

insert into gciweb.municipios(municipio, id_edp) values ('Cachoeira Paulista', 1)

insert into gciweb.subestacoes(nome, sigla, id_municipio, id_edp) values ('Guarulhos', 'GUR', 1, 1)
insert into gciweb.subestacoes(nome, sigla, id_municipio, id_edp) values ('Bento Ferreira', 'BFE',3, 2)

Go

insert into gciweb.circuitos(circuito, id_subestacao, id_edp, tensao) values ('RGUL0102', 1, 1, 13.8)
insert into gciweb.circuitos(circuito, id_subestacao, id_edp, tensao) values ('BFE01', 2, 2, 11.4)

Go

insert into gciweb.regionais(regional, id_edp) values ('Guarulhos', 1)
insert into gciweb.regionais(regional, id_edp) values ('Fundo do Vale', 1)
insert into gciweb.regionais(regional, id_edp) values ('Grande Vitoria', 2)
insert into gciweb.regionais(regional, id_edp) values ('Sul', 2)

Go


insert into gciweb.tipo_viabilidade(descricao) values ('Or�amento Estimado')
insert into gciweb.tipo_viabilidade(descricao) values ('Estudo de Viabilidade')
insert into gciweb.tipo_viabilidade(descricao) values ('Anteprojeto')

Go

insert into gciweb.tipo_analise(analise) values ('Carga')
insert into gciweb.tipo_analise(analise) values ('Gera��o')
insert into gciweb.tipo_analise(analise) values ('POA')


Go

insert into gciweb.tipo_pedido(descricao) values ('Aumento de Demanda')
insert into gciweb.tipo_pedido(descricao) values ('Liga��o Nova')
insert into gciweb.tipo_pedido(descricao) values ('MMGD')
insert into gciweb.tipo_pedido(descricao) values ('Autoprodutor')
insert into gciweb.tipo_pedido(descricao) values ('Produtor Independente')
insert into gciweb.tipo_pedido(descricao) values ('Outros')

Go

insert into gciweb.usuarios(matricula, nome, email, admin, visualizar, criar, editar, deletar, bloqueado) values ('7034', 'Jader Kayque Marques de Campos', '', 1, 1, 1, 1, 1, 0)
insert into gciweb.usuarios(matricula, nome, email, admin, visualizar, criar, editar, deletar, bloqueado) values ('EX160187', 'Giovana da Penha Rocha', '', 1, 1, 1, 1, 1, 0)
insert into gciweb.usuarios(matricula, nome, email, admin, visualizar, criar, editar, deletar, bloqueado) values ('E712208', 'Lucas Nascimento da Silva', '', 1, 1, 1, 1, 1, 0)


Go 


insert into gciweb.empresas(nome_empresa, cnpj) values ('Empresa Teste', '00111222000101')

go 

insert into gciweb.socios(nome, cargo, id_empresa) values ('Socio Teste', 'Gestor', 1)

Go

insert into gciweb.status_tipos(status, descricao, ativo) values ('Conclu�do', 'Conclu�do', 1)
insert into gciweb.status_tipos(status, descricao, ativo) values ('Em andamento', 'Em Andamento', 1)


go 

insert into gciweb.resp_regioes (id_regional, id_usuario, ano_ref) values (1, 1, 2025)

Go

insert into gciweb.estudos ([num_doc],[protocolo],[nome_projeto],[descricao],[instalacao],[n_alternativas]
      ,[dem_solicit_fp],[dem_solicit_p],[id_edp],[id_regional]
      ,[id_criado_por],[id_resp_regiao],[id_municipio],[id_tipo_viab],[id_tipo_analise],[id_tipo_pedido],[data_registro],[data_criacao],[data_transgressao],[data_vencimento]) 
	  values ('0001/25', '', 'Projeto Teste 1', '', '', 0, 1000, 1000, 1, 1, 1, 1, 1, 1, 1, 1, '2025-08-15', '2025-08-15', '2025-08-15', '2025-08-15')

Go


insert into gciweb.status_estudo(data, id_status_tipo, observacao, id_estudo, id_criado_por) values ('2025-08-15',1, '', 1, 1)

Go





insert into [gciweb].[alternativas] ([id_circuito],[descricao],[dem_fp_ant],[dem_p_ant],[dem_fp_dep],[dem_p_dep],[flag_menor_custo_global],[flag_alternativa_escolhida],[custo_modular],[id_estudo])
									values (1, 'alternativa 1', 500, 500, 1000, 1000, 1, 1, 50000, 1)

Go

insert into [gciweb].anexos (nome_arquivo, endereco, data_upload, id_estudo) values ('arquivo 1.pdf', 'pasta/arquivo 1.pdf', '2025-08-15', 1)
 



 -- RESETA O ID AUTOMATICO DA TABELA ESCOLHIDA
--delete from gciweb.anexos
--DBCC CHECKIDENT ('gciweb.[anexos]', RESEED, 0)