create schema gciweb
Go

-- Schema otimizado para SQL SERVER com BIGINT IDENTITY
-- Todos os tipos de dados são nativos do SQL Server 2016+
-- Sistema centralizado, BIGINT é mais adequado que UNIQUEIDENTIFIER

CREATE TABLE "gciweb"."FATOR_K"(
    "id_k" BIGINT IDENTITY(1,1) NOT NULL,
    "k" decimal(6,2) NULL,
    "kg" decimal(6,2) NULL,
    "subgrupo_tarif" varchar(3) NOT NULL,
	"data_ref" DATE NOT NULL,
    "id_edp" BIGINT NOT NULL
);

ALTER TABLE "gciweb"."FATOR_K" ADD CONSTRAINT "gciweb_fator_k_id_primary" PRIMARY KEY("id_k")

CREATE TABLE "gciweb"."edp"(
    "id_edp" BIGINT IDENTITY(1,1) NOT NULL,
    "empresa" VARCHAR(2) NOT NULL
);
ALTER TABLE "gciweb"."edp" ADD CONSTRAINT "gciweb_edp_id_edp_primary" PRIMARY KEY("id_edp");

CREATE TABLE "gciweb"."usuarios"(
    "id_usuario" BIGINT IDENTITY(1,1) NOT NULL,
    "matricula" VARCHAR(255) NOT NULL UNIQUE,
    "nome" TEXT NOT NULL,
    "email" TEXT NULL,
    "admin" BIT NOT NULL,
    "visualizar" BIT NOT NULL,
    "criar" BIT NOT NULL,
    "editar" BIT NOT NULL,
    "deletar" BIT NOT NULL,
    "bloqueado" BIT NOT NULL DEFAULT 0,
    "id_edp" BIGINT NOT NULL DEFAULT 1
);
ALTER TABLE "gciweb"."usuarios" ADD CONSTRAINT "gciweb_usuarios_id_usuario_primary" PRIMARY KEY("id_usuario");

CREATE TABLE "gciweb"."resp_regioes"(
	"id_resp_regiao" BIGINT IDENTITY(1,1) NOT NULL,
	"id_regional" BIGINT NOT NULL,
	"id_usuario" BIGINT NOT NULL,
	"ano_ref" INT NOT NULL
);

ALTER TABLE "gciweb"."resp_regioes" ADD CONSTRAINT "gciweb_resp_regioes_id_resp_regiao_primary" PRIMARY KEY("id_resp_regiao");


CREATE TABLE "gciweb"."empresas"(
    "id_empresa" BIGINT IDENTITY(1,1) NOT NULL,
    "nome_empresa" VARCHAR(255) NOT NULL,
    "cnpj" VARCHAR(14) NOT NULL UNIQUE, -- Tamanho fixo do CNPJ
    "abertura" DATE NULL,
    "situacao" VARCHAR(255) NULL,
    "tipo" VARCHAR(255) NULL,
    "porte" VARCHAR(255) NULL,
    "natureza_juridica" VARCHAR(255) NULL,
    "logradouro" VARCHAR(255) NULL,
    "numero" VARCHAR(10) NULL,
    "complemento" VARCHAR(255) NULL,
    "municipio" VARCHAR(255) NULL,
    "bairro" VARCHAR(255) NULL,
    "uf" CHAR(2) NULL,
    "cep" VARCHAR(8) NULL,
    "email" VARCHAR(255) NULL,
    "telefone" VARCHAR(20) NULL,
    "data_situacao" DATE NULL,
    "ultima_atualizacao" DATETIME NULL,
    "status" VARCHAR(255) NULL,
    "fantasia" VARCHAR(255) NULL,
    "efr" VARCHAR(255) NULL,
    "motivo_situacao" VARCHAR(255) NULL,
    "situacao_especial" VARCHAR(255) NULL,
    "data_situacao_especial" DATE NULL
);
ALTER TABLE "gciweb"."empresas" ADD CONSTRAINT "gciweb_empresas_id_empresa_primary" PRIMARY KEY("id_empresa");

CREATE TABLE "gciweb"."regionais"(
    "id_regional" BIGINT IDENTITY(1,1) NOT NULL,
    "regional" VARCHAR(255) NOT NULL,
    "id_edp" BIGINT NOT NULL
);
ALTER TABLE "gciweb"."regionais" ADD CONSTRAINT "gciweb_regionais_id_regional_primary" PRIMARY KEY("id_regional");

CREATE TABLE "gciweb"."municipios"(
    "id_municipio" BIGINT IDENTITY(1,1) NOT NULL,
    "municipio" VARCHAR(255) NOT NULL,
    "id_edp" BIGINT NOT NULL
);
ALTER TABLE "gciweb"."municipios" ADD CONSTRAINT "gciweb_municipios_id_municipio_primary" PRIMARY KEY("id_municipio");

CREATE TABLE "gciweb"."subestacoes"(
    "id_subestacao" BIGINT IDENTITY(1,1) NOT NULL,
    "nome" VARCHAR(255) NOT NULL,
    "sigla" VARCHAR(10) NOT NULL,
    "id_municipio" BIGINT NOT NULL,
    "id_edp" BIGINT NOT NULL
);
ALTER TABLE "gciweb"."subestacoes" ADD CONSTRAINT "gciweb_subestacoes_id_subestacao_primary" PRIMARY KEY("id_subestacao");

CREATE TABLE "gciweb"."circuitos"(
    "id_circuito" BIGINT IDENTITY(1,1) NOT NULL,
    "circuito" VARCHAR(255) NOT NULL,
    "id_subestacao" BIGINT NULL,
    "id_edp" BIGINT NOT NULL,
    "tensao" VARCHAR(20) NOT NULL
);
ALTER TABLE "gciweb"."circuitos" ADD CONSTRAINT "gciweb_circuitos_id_circuito_primary" PRIMARY KEY("id_circuito");

--CREATE TABLE "gciweb"."tipo_viabilidade"(
--    "id_tipo_viab" BIGINT IDENTITY(1,1) NOT NULL,
--    "descricao" VARCHAR(255) NOT NULL
--);
--ALTER TABLE "gciweb"."tipo_viabilidade" ADD CONSTRAINT "gciweb_tipo_viabilidade_id_tipo_viab_primary" PRIMARY KEY("id_tipo_viab");
--
--CREATE TABLE "gciweb"."tipo_analise"(
--    "id_tipo_analise" BIGINT IDENTITY(1,1) NOT NULL,
--    "analise" VARCHAR(255) NOT NULL
--);
--ALTER TABLE "gciweb"."tipo_analise" ADD CONSTRAINT "gciweb_tipo_analise_id_tipo_analise_primary" PRIMARY KEY("id_tipo_analise");
--
--CREATE TABLE "gciweb"."tipo_pedido"(
--    "id_tipo_pedido" BIGINT IDENTITY(1,1) NOT NULL,
--    "descricao" VARCHAR(255) NOT NULL
--);
--ALTER TABLE "gciweb"."tipo_pedido" ADD CONSTRAINT "gciweb_tipo_pedido_id_tipo_pedido_primary" PRIMARY KEY("id_tipo_pedido");


 -- CRIADO TIPO_SOLICITACAO para substituir Tipo_analise, Tipo_pedido e tipo_viabilidade em uma única tabela.
CREATE TABLE "gciweb"."tipo_solicitacao"(
    "id_tipo_solicitacao" BIGINT IDENTITY(1,1) NOT NULL,
    "viabilidade" VARCHAR(255) NOT NULL,
    "analise" VARCHAR(255) NOT NULL,
    "pedido" VARCHAR(255) NOT NULL
);
ALTER TABLE "gciweb"."tipo_solicitacao" ADD CONSTRAINT "gciweb_tipo_solicitacao_id_tipo_solicitacao_primary" PRIMARY KEY("id_tipo_solicitacao");

CREATE TABLE "gciweb"."estudos"(
    "id_estudo" BIGINT IDENTITY(1,1) NOT NULL,
    "num_doc" VARCHAR(255) NOT NULL,
    "protocolo" BIGINT NULL,
    "nome_projeto" TEXT NOT NULL,
    "descricao" TEXT NULL,
    "instalacao" BIGINT NULL,
    "n_alternativas" INT NOT NULL DEFAULT 0,
    -- Demandas atual e solicitada pelo cliente
    "dem_carga_atual_fp" DECIMAL(10,2) NOT NULL DEFAULT 0,
    "dem_carga_atual_p" DECIMAL(10,2) NOT NULL DEFAULT 0,
	"dem_carga_solicit_fp" DECIMAL(10,2) NOT NULL DEFAULT 0,
    "dem_carga_solicit_p" DECIMAL(10,2) NOT NULL DEFAULT 0,
    "dem_ger_atual_fp" DECIMAL(10,2) NOT NULL DEFAULT 0,
    "dem_ger_atual_p" DECIMAL(10,2) NOT NULL DEFAULT 0,
	"dem_ger_solicit_fp" DECIMAL(10,2) NOT NULL DEFAULT 0,
    "dem_ger_solicit_p" DECIMAL(10,2) NOT NULL DEFAULT 0,
    "latitude_cliente" DECIMAL(10,8) NULL, -- Melhor para coordenadas
    "longitude_cliente" DECIMAL(11,8) NULL, -- Melhor para coordenadas
    "livre" BIT NULL,
    "observacao" TEXT NULL,
    "id_edp" BIGINT NOT NULL,
    "id_regional" BIGINT NOT NULL,
    "id_criado_por" BIGINT NOT NULL,
    "id_resp_regiao" BIGINT NOT NULL,
    "id_empresa" BIGINT NULL,
    "id_municipio" BIGINT NOT NULL,
    "id_tipo_solicitacao" BIGINT NOT NULL,
    "data_registro" DATE NOT NULL DEFAULT GETDATE(),
    "data_abertura_cliente" DATE NULL ,
    "data_desejada_cliente" DATE NULL,
    "data_vencimento_cliente" DATE NULL,
    "data_prevista_conexao" DATE NULL,
    "data_vencimento_ddpe" DATE NULL

);
ALTER TABLE "gciweb"."estudos" ADD CONSTRAINT "gciweb_estudos_id_estudo_primary" PRIMARY KEY("id_estudo");
CREATE INDEX "gciweb_estudos_num_doc_index" ON "gciweb"."estudos"("num_doc");
CREATE INDEX "gciweb_estudos_data_criacao_index" ON "gciweb"."estudos"("data_criacao");

CREATE TABLE "gciweb"."anexos"(
    "id_anexo" BIGINT IDENTITY(1,1) NOT NULL,
    "nome_arquivo" VARCHAR(255) NOT NULL,
    "endereco" VARCHAR(500) NOT NULL,
    "tamanho_arquivo" BIGINT NULL, -- Adicionado campo útil
    "tipo_mime" VARCHAR(100) NULL, -- Adicionado campo útil
    "data_upload" DATETIME NOT NULL DEFAULT GETDATE(),
    "id_estudo" BIGINT NOT NULL
);
ALTER TABLE "gciweb"."anexos" ADD CONSTRAINT "gciweb_anexos_id_anexo_primary" PRIMARY KEY("id_anexo");

CREATE TABLE "gciweb"."socios"(
    "id_socios" BIGINT IDENTITY(1,1) NOT NULL,
    "nome" VARCHAR(255) NOT NULL,
    "cargo" VARCHAR(255) NULL,
    "id_empresa" BIGINT NOT NULL
);
ALTER TABLE "gciweb"."socios" ADD CONSTRAINT "gciweb_socios_id_socios_primary" PRIMARY KEY("id_socios");


CREATE TABLE "gciweb"."status_estudo"(
    "id_status" BIGINT IDENTITY(1,1) NOT NULL,
    "data" DATETIME NOT NULL DEFAULT GETDATE(),
    "id_status_tipo" BIGINT NOT NULL,
    "observacao" TEXT NULL,
    "id_estudo" BIGINT NOT NULL,
    "id_criado_por" BIGINT NOT NULL
);

ALTER TABLE "gciweb"."status_estudo" ADD CONSTRAINT "gciweb_status_estudo_id_status_primary" PRIMARY KEY("id_status");

CREATE TABLE "gciweb"."kits"(
    "id_kit" BIGINT IDENTITY(1,1) NOT NULL,
    "kit" VARCHAR(255) NOT NULL,
    "tipo" VARCHAR(100) NOT NULL,
    "descricao" VARCHAR(500) NOT NULL,
    "valor_unit" DECIMAL(15,2) NOT NULL, -- Melhor para valores monetários
    "ano_ref" INT NOT NULL,
    "ativo" BIT NOT NULL DEFAULT 1 -- Campo para controle
);
ALTER TABLE "gciweb"."kits" ADD CONSTRAINT "gciweb_kits_id_kit_primary" PRIMARY KEY("id_kit");

CREATE TABLE "gciweb"."alternativas"(
    "id_alternativa" BIGINT IDENTITY(1,1) NOT NULL,
    "id_circuito" BIGINT NOT NULL,
    "descricao" TEXT NOT NULL,
    "dem_carga_fp_dep" DECIMAL(10,2) NOT NULL,
    "dem_carga_p_dep" DECIMAL(10,2) NOT NULL,
    "dem_ger_fp_dep" DECIMAL(10,2) NOT NULL,
    "dem_ger_p_dep" DECIMAL(10,2) NOT NULL,
    "latitude_ponto_conexao" DECIMAL(10,8) NULL,
    "longitude_ponto_conexao" DECIMAL(11,8) NULL,
    "flag_menor_custo_global" BIT NOT NULL DEFAULT 0,
    "flag_alternativa_escolhida" BIT NOT NULL DEFAULT 0,
    "custo_modular" DECIMAL(15,2) NOT NULL,
    "id_obra" BIGINT NULL,
    "id_estudo" BIGINT NOT NULL,
    "blob_image" TEXT NULL,
    "observacao" TEXT NULL,
    "ERD" DECIMAL(10,3) NULL,
    "demanda_disponivel_ponto" DECIMAL(10,2) NULL
    "flag_carga" bit null,
    "flag_geracao" bit null,
    "flag_fluxo_reverso" bit null,
    "letra_alternativa" varchar(1) null,
    "proporcionalidade" decimal(3,2),
    "id_k" BIGINT null,
    'id_img_anexo' BIGINT null,


);

ALTER TABLE "gciweb"."alternativas" ADD CONSTRAINT "gciweb_alternativas_id_alternativa_primary" PRIMARY KEY("id_alternativa");

CREATE TABLE "gciweb"."obras"(
    "id_obra" BIGINT IDENTITY(1,1) NOT NULL,
    "quantidade" DECIMAL(10,3) NOT NULL,
    "descricao" VARCHAR(500) NOT NULL,
    "valor" DECIMAL(15,2) NOT NULL,
    "id_regional" BIGINT NOT NULL,
    "id_kit" BIGINT NOT NULL,
    "id_alternativa" BIGINT NOT NULL
);
ALTER TABLE "gciweb"."obras" ADD CONSTRAINT "gciweb_obras_id_obra_primary" PRIMARY KEY("id_obra");

CREATE TABLE "gciweb"."status_tipos"(
    "id_status_tipo" BIGINT IDENTITY(1,1) NOT NULL,
    "status" VARCHAR(100) NOT NULL,
    "descricao" TEXT NULL,
    "ativo" BIT NOT NULL DEFAULT 1
);
ALTER TABLE "gciweb"."status_tipos" ADD CONSTRAINT "gciweb_status_tipos_id_primary" PRIMARY KEY("id_status_tipo");

-- FOREIGN KEY CONSTRAINTS
ALTER TABLE "gciweb"."regionais" ADD CONSTRAINT "gciweb_regionais_id_edp_foreign" FOREIGN KEY("id_edp") REFERENCES "gciweb"."edp"("id_edp");
ALTER TABLE "gciweb"."municipios" ADD CONSTRAINT "gciweb_municipios_id_edp_foreign" FOREIGN KEY("id_edp") REFERENCES "gciweb"."edp"("id_edp");
ALTER TABLE "gciweb"."subestacoes" ADD CONSTRAINT "gciweb_subestacoes_id_edp_foreign" FOREIGN KEY("id_edp") REFERENCES "gciweb"."edp"("id_edp");
ALTER TABLE "gciweb"."subestacoes" ADD CONSTRAINT "gciweb_subestacoes_id_municipio_foreign" FOREIGN KEY("id_municipio") REFERENCES "gciweb"."municipios"("id_municipio");
ALTER TABLE "gciweb"."circuitos" ADD CONSTRAINT "gciweb_circuitos_id_subestacao_foreign" FOREIGN KEY("id_subestacao") REFERENCES "gciweb"."subestacoes"("id_subestacao");
ALTER TABLE "gciweb"."circuitos" ADD CONSTRAINT "gciweb_circuitos_id_edp_foreign" FOREIGN KEY("id_edp") REFERENCES "gciweb"."edp"("id_edp");

ALTER TABLE "gciweb"."resp_regioes" ADD CONSTRAINT "gciweb_resp_regioes_id_usuario_foreign" FOREIGN KEY("id_usuario") REFERENCES "gciweb"."usuarios"("id_usuario");
ALTER TABLE "gciweb"."resp_regioes" ADD CONSTRAINT "gciweb_regioes_id_regional_foreign" FOREIGN KEY("id_regional") REFERENCES "gciweb"."regionais"("id_regional");

ALTER TABLE "gciweb"."estudos" ADD CONSTRAINT "gciweb_estudos_id_edp_foreign" FOREIGN KEY("id_edp") REFERENCES "gciweb"."edp"("id_edp");
ALTER TABLE "gciweb"."estudos" ADD CONSTRAINT "gciweb_estudos_id_regional_foreign" FOREIGN KEY("id_regional") REFERENCES "gciweb"."regionais"("id_regional");
ALTER TABLE "gciweb"."estudos" ADD CONSTRAINT "gciweb_estudos_id_criado_por_foreign" FOREIGN KEY("id_criado_por") REFERENCES "gciweb"."usuarios"("id_usuario");
ALTER TABLE "gciweb"."estudos" ADD CONSTRAINT "gciweb_estudos_id_eng_responsavel_foreign" FOREIGN KEY("id_resp_regiao") REFERENCES "gciweb"."resp_regioes"("id_resp_regiao");
ALTER TABLE "gciweb"."estudos" ADD CONSTRAINT "gciweb_estudos_id_empresa_foreign" FOREIGN KEY("id_empresa") REFERENCES "gciweb"."empresas"("id_empresa");
ALTER TABLE "gciweb"."estudos" ADD CONSTRAINT "gciweb_estudos_id_municipio_foreign" FOREIGN KEY("id_municipio") REFERENCES "gciweb"."municipios"("id_municipio");
ALTER TABLE "gciweb"."estudos" ADD CONSTRAINT "gciweb_estudos_id_tipo_solicitacao_foreign" FOREIGN KEY("id_tipo_solicitacao") REFERENCES "gciweb"."tipo_solicitacao"("id_tipo_solicitacao");

ALTER TABLE "gciweb"."anexos" ADD CONSTRAINT "gciweb_anexos_id_estudo_foreign" FOREIGN KEY("id_estudo") REFERENCES "gciweb"."estudos"("id_estudo");
ALTER TABLE "gciweb"."socios" ADD CONSTRAINT "gciweb_socios_id_empresa_foreign" FOREIGN KEY("id_empresa") REFERENCES "gciweb"."empresas"("id_empresa");
ALTER TABLE "gciweb"."status_estudo" ADD CONSTRAINT "gciweb_status_estudo_id_estudo_foreign" FOREIGN KEY("id_estudo") REFERENCES "gciweb"."estudos"("id_estudo");
ALTER TABLE "gciweb"."status_estudo" ADD CONSTRAINT "gciweb_status_estudo_id_criado_por_foreign" FOREIGN KEY("id_criado_por") REFERENCES "gciweb"."usuarios"("id_usuario");
ALTER TABLE "gciweb"."status_estudo" ADD CONSTRAINT "gciweb_status_estudo_id_status_tipo_foreign" FOREIGN KEY("id_status_tipo") REFERENCES "gciweb"."status_tipos"("id_status_tipo");

ALTER TABLE "gciweb"."alternativas" ADD CONSTRAINT "gciweb_alternativas_id_circuito_foreign" FOREIGN KEY("id_circuito") REFERENCES "gciweb"."circuitos"("id_circuito");
ALTER TABLE "gciweb"."alternativas" ADD CONSTRAINT "gciweb_alternativas_id_estudo_foreign" FOREIGN KEY("id_estudo") REFERENCES "gciweb"."estudos"("id_estudo");
ALTER TABLE "gciweb"."alternativas" ADD CONSTRAINT "gciweb_alternativas_id_anexo_foreign" FOREIGN KEY("id_img_anexo") REFERENCES "gciweb"."anexos"("id_anexo");

ALTER TABLE "gciweb"."obras" ADD CONSTRAINT "gciweb_obras_id_regional_foreign" FOREIGN KEY("id_regional") REFERENCES "gciweb"."regionais"("id_regional");
ALTER TABLE "gciweb"."obras" ADD CONSTRAINT "gciweb_obras_id_kit_foreign" FOREIGN KEY("id_kit") REFERENCES "gciweb"."kits"("id_kit");
ALTER TABLE "gciweb"."obras" ADD CONSTRAINT "gciweb_obras_id_alternativa_foreign" FOREIGN KEY("id_alternativa") REFERENCES "gciweb"."alternativas"("id_alternativa");
ALTER TABLE "gciweb"."alternativas" ADD CONSTRAINT "gciweb_alternativas_id_obra_foreign" FOREIGN KEY("id_obra") REFERENCES "gciweb"."obras"("id_obra");
ALTER TABLE "gciweb"."alternativas" ADD CONSTRAINT "gciweb_alternativas_id_k_foreign" FOREIGN KEY("id_k") REFERENCES "gciweb"."FATOR_K"("id_k");
ALTER TABLE "gciweb"."FATOR_K" ADD CONSTRAINT "gciweb_fator_k_id_edp_foreign" FOREIGN KEY("id_edp") REFERENCES "gciweb"."edp"("id_edp")

ALTER TABLE "gciweb.usuarios" ADD CONSTRAINT "gciweb_usuarios_id_edp_foreign" FOREIGN KEY("id_edp") REFERENCES "gciweb"."edp"("id_edp");


-- ÍNDICES ADICIONAIS PARA PERFORMANCE
CREATE INDEX "idx_estudos_empresa" ON "gciweb"."estudos"("id_empresa");
CREATE INDEX "idx_estudos_eng_responsavel" ON "gciweb"."estudos"("id_resp_regiao");
CREATE INDEX "idx_estudos_regional" ON "gciweb"."estudos"("id_regional");
CREATE INDEX "idx_alternativas_estudo" ON "gciweb"."alternativas"("id_estudo");
CREATE INDEX "idx_status_estudo_data" ON "gciweb"."status_estudo"("data");
CREATE INDEX "idx_anexos_estudo" ON "gciweb"."anexos"("id_estudo");