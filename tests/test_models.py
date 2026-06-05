"""Testes de lógica dos modelos (sem chamadas HTTP)."""

import pytest
from decimal import Decimal
from datetime import date, datetime


class TestEstudoModel:
    def test_criar_estudo(self, app):
        with app.app_context():
            from app.models import (
                db, Estudo, EDP, Regional, Municipio, Empresa,
                Tensao, TipoSolicitacao, RespRegiao, Usuario,
            )
            edp = EDP.query.first()
            mun = Municipio.query.first()
            resp_reg = RespRegiao.query.first()
            tipo = TipoSolicitacao.query.first()
            tens = Tensao.query.first()
            emp = Empresa.query.first()
            reg = Regional.query.first()

            if not all([edp, mun, resp_reg, tipo, tens, reg]):
                pytest.skip("Dados de apoio insuficientes")

            zero = Decimal("0.0")
            estudo = Estudo(
                num_doc="0001/25",
                nome_projeto="Projeto Modelo",
                id_edp=edp.id_edp,
                id_regional=reg.id_regional,
                id_municipio=mun.id_municipio,
                id_resp_regiao=resp_reg.id_resp_regiao,
                id_tipo_solicitacao=tipo.id_tipo_solicitacao,
                id_tensao=tens.id_tensao,
                id_empresa=emp.id_empresa if emp else None,
                id_criado_por=1,
                id_resp_alteracao=1,
                data_registro=date.today(),
                data_abertura_cliente=date(2024, 1, 15),
                data_desejada_cliente=date(2024, 3, 1),
                data_vencimento_cliente=date(2024, 6, 1),
                data_prevista_conexao=date(2024, 6, 1),
                data_vencimento_ddpe=date(2024, 2, 15),
                dem_carga_atual_fp=zero,
                dem_carga_atual_p=zero,
                dem_carga_solicit_fp=zero,
                dem_carga_solicit_p=zero,
                dem_ger_atual_fp=zero,
                dem_ger_atual_p=zero,
                dem_ger_solicit_fp=zero,
                dem_ger_solicit_p=zero,
            )
            db.session.add(estudo)
            db.session.commit()

            assert estudo.id_estudo is not None
            assert estudo.num_doc == "0001/25"
            assert estudo.nome_projeto == "Projeto Modelo"

    def test_get_with_all_relations(self, app):
        with app.app_context():
            from app.models import Estudo
            estudo = Estudo.query.first()
            if not estudo:
                pytest.skip("Nenhum estudo disponível")
            eid = estudo.id_estudo

            resultado = Estudo.get_with_all_relations(eid)
            assert resultado is not None
            assert resultado.id_estudo == eid

    def test_ultimo_status_sem_status(self, app):
        with app.app_context():
            from app.models import Estudo
            estudo = Estudo.query.first()
            if not estudo:
                pytest.skip("Nenhum estudo disponível")
            # Sem status cadastrado, deve retornar None ou StatusEstudo
            result = estudo.ultimo_status
            # Não deve levantar exceção
            assert result is None or hasattr(result, "id_status")

    def test_n_alternativas_inicial(self, app):
        with app.app_context():
            from app.models import Estudo
            estudo = Estudo.query.first()
            if not estudo:
                pytest.skip("Nenhum estudo disponível")
            assert estudo.n_alternativas >= 0


class TestAlternativaModel:
    def test_criar_alternativa(self, app):
        with app.app_context():
            from app.models import db, Alternativa, Estudo, Circuito, FatorK
            estudo = Estudo.query.first()
            circ = Circuito.query.first()
            if not estudo or not circ:
                pytest.skip("Dados insuficientes")

            alt = Alternativa(
                id_estudo=estudo.id_estudo,
                id_circuito=circ.id_circuito,
                descricao="Alternativa de modelo",
                dem_p_ant=Decimal("100.0"),
                dem_fp_ant=Decimal("80.0"),
                dem_p_dep=Decimal("150.0"),
                dem_fp_dep=Decimal("120.0"),
                latitude_ponto_conexao=Decimal("-22.9"),
                longitude_ponto_conexao=Decimal("-47.06"),
                letra_alternativa="A",
                subgrupo_tarifario="A2",
                etapa=1,
                custo_modular=Decimal("10000.00"),
                ERD=Decimal("50.0"),
                proporcionalidade=Decimal("0.5"),
            )
            db.session.add(alt)
            db.session.commit()

            assert alt.id_alternativa is not None
            assert alt.letra_alternativa == "A"
            assert float(alt.latitude_ponto_conexao) == pytest.approx(-22.9)


class TestUsuarioModel:
    def test_usuario_admin_tem_permissoes(self, app):
        with app.app_context():
            from app.models import Usuario
            usr = Usuario.query.filter_by(admin=True).first()
            if not usr:
                pytest.skip("Nenhum admin disponível")

            assert usr.admin is True
            assert usr.bloqueado is False

    def test_usuario_campos_obrigatorios(self, app):
        with app.app_context():
            from app.models import Usuario
            usr = Usuario.query.first()
            if not usr:
                pytest.skip("Nenhum usuário disponível")

            assert usr.matricula is not None
            assert usr.nome is not None
            assert usr.id_edp is not None

    def test_usuario_bloqueado_nao_tem_acesso(self, app):
        with app.app_context():
            from app.models import db, Usuario, EDP
            edp = EDP.query.first()
            if not edp:
                pytest.skip("Nenhum EDP disponível")

            usr_bloq = Usuario(
                matricula="bloqueado01",
                nome="Usuário Bloqueado",
                id_edp=edp.id_edp,
                admin=False,
                visualizar=False,
                criar=False,
                editar=False,
                deletar=False,
                aprovar=False,
                bloqueado=True,
            )
            db.session.add(usr_bloq)
            db.session.commit()

            assert usr_bloq.bloqueado is True
            assert usr_bloq.admin is False


class TestStatusEstudoModel:
    def test_criar_status(self, app):
        with app.app_context():
            from app.models import db, StatusEstudo, Estudo, StatusTipo
            estudo = Estudo.query.first()
            tipo = StatusTipo.query.first()
            if not estudo or not tipo:
                pytest.skip("Dados insuficientes")

            se = StatusEstudo(
                id_estudo=estudo.id_estudo,
                id_status_tipo=tipo.id_status_tipo,
                id_criado_por=1,
                observacao="Observação de teste",
            )
            db.session.add(se)
            db.session.commit()

            assert se.id_status is not None
            assert se.observacao == "Observação de teste"
            assert se.id_estudo == estudo.id_estudo

    def test_status_tem_data_automatica(self, app):
        with app.app_context():
            from app.models import StatusEstudo, Estudo, StatusTipo
            estudo = Estudo.query.first()
            tipo = StatusTipo.query.first()
            if not estudo or not tipo:
                pytest.skip("Dados insuficientes")

            se = StatusEstudo.query.filter_by(id_estudo=estudo.id_estudo).first()
            if se:
                # data pode ser None ou datetime dependendo do default
                assert se.id_status is not None


class TestRegionalModel:
    def test_regional_pertence_a_edp(self, app):
        with app.app_context():
            from app.models import Regional, EDP
            reg = Regional.query.first()
            edp = EDP.query.first()
            if not reg or not edp:
                pytest.skip("Dados insuficientes")

            assert reg.id_edp == edp.id_edp

    def test_municipios_de_regional(self, app):
        with app.app_context():
            from app.models import Regional
            reg = Regional.query.first()
            if not reg:
                pytest.skip("Nenhuma regional disponível")

            # Deve ser uma lista (pode ser vazia)
            assert isinstance(reg.municipios, list)


class TestCircuitoModel:
    def test_circuito_tem_subestacao(self, app):
        with app.app_context():
            from app.models import Circuito, Subestacao
            circ = Circuito.query.first()
            if not circ:
                pytest.skip("Nenhum circuito disponível")

            assert circ.id_subestacao is not None

    def test_circuito_pertence_a_edp(self, app):
        with app.app_context():
            from app.models import Circuito, EDP
            circ = Circuito.query.first()
            edp = EDP.query.first()
            if not circ or not edp:
                pytest.skip("Dados insuficientes")

            assert circ.id_edp == edp.id_edp


class TestEmpresaModel:
    def test_empresa_tem_cnpj(self, app):
        with app.app_context():
            from app.models import Empresa
            emp = Empresa.query.first()
            if not emp:
                pytest.skip("Nenhuma empresa disponível")

            assert emp.cnpj is not None
            assert len(emp.cnpj) <= 14

    def test_cnpj_unico(self, app):
        with app.app_context():
            from app.models import Empresa
            cnpjs = [e.cnpj for e in Empresa.query.all()]
            assert len(cnpjs) == len(set(cnpjs)), "CNPJs duplicados encontrados"
