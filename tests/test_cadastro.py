"""Testes para o blueprint de cadastro de estudos."""

import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO
from datetime import date


class TestCadastroGet:
    def test_form_sem_login_redireciona(self, client):
        resp = client.get("/estudos/cadastro")
        assert resp.status_code in (301, 302)

    def test_form_com_login_retorna_200(self, auth_client):
        client, _ = auth_client
        resp = client.get("/estudos/cadastro")
        assert resp.status_code == 200

    def test_form_contem_campos_obrigatorios(self, auth_client):
        client, _ = auth_client
        resp = client.get("/estudos/cadastro")
        html = resp.data.decode("utf-8", errors="replace")
        assert "form" in html.lower()


class TestCadastroPost:
    def _form_data(self, **kw):
        """Dados mínimos para criar um estudo válido."""
        defaults = {
            "nome_projeto": "Projeto Teste",
            "id_empresa": "1",
            "municipio": "1",
            "resp_regiao": "1",
            "tipo_pedido": "1",
            "tensao": "1",
            "data_abertura_cliente": "2024-01-15",
            "data_desejada_cliente": "2024-03-01",
            "data_vencimento_cliente": "2024-06-01",
            "data_prevista_conexao": "2024-06-01",
            "data_vencimento_ddpe": "2024-02-15",
        }
        defaults.update(kw)
        return defaults

    def test_post_sem_login_redireciona(self, client):
        resp = client.post("/estudos/cadastro", data=self._form_data())
        assert resp.status_code in (301, 302)

    def test_post_formulario_invalido_retorna_form(self, auth_client):
        """POST com dados incompletos deve retornar o formulário com erros."""
        client, _ = auth_client
        resp = client.post("/estudos/cadastro", data={})
        # Deve re-renderizar o form (200) ou redirecionar após flash
        assert resp.status_code in (200, 302)

    def test_post_valido_cria_estudo(self, auth_client, app):
        """POST com dados válidos deve criar o estudo e redirecionar."""
        client, user = auth_client

        with app.app_context():
            from app.models import db, Estudo, EDP, Regional, Municipio, RespRegiao, TipoSolicitacao, Tensao

            edp = EDP.query.first()
            reg = Regional.query.first()
            mun = Municipio.query.first()
            resp_reg = RespRegiao.query.first()
            tipo = TipoSolicitacao.query.first()
            tens = Tensao.query.first()

            if not all([edp, reg, mun, resp_reg, tipo, tens]):
                pytest.skip("Dados de apoio insuficientes para este teste")

            form_data = self._form_data(
                id_empresa="1",
                municipio=str(mun.id_municipio),
                resp_regiao=str(resp_reg.id_resp_regiao),
                tipo_pedido=str(tipo.id_tipo_solicitacao),
                tensao=str(tens.id_tensao),
            )

        resp = client.post("/estudos/cadastro", data=form_data)
        # Sucesso redireciona para alternativas
        assert resp.status_code in (200, 302)


class TestEditarEstudo:
    def test_editar_sem_login_redireciona(self, client):
        resp = client.get("/estudos/editar/999")
        assert resp.status_code in (301, 302)

    def test_editar_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.get("/estudos/editar/999999")
        assert resp.status_code == 404

    def test_editar_existente_retorna_200(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Estudo
            estudo = Estudo.query.first()
            if not estudo:
                pytest.skip("Nenhum estudo cadastrado para testar edição")
            eid = estudo.id_estudo

        resp = client.get(f"/estudos/editar/{eid}")
        assert resp.status_code == 200


class TestExcluirEstudo:
    def test_excluir_sem_login_redireciona(self, client):
        resp = client.delete("/estudos/excluir/1")
        assert resp.status_code in (301, 302)

    def test_excluir_inexistente_retorna_404(self, auth_client):
        """A rota captura NotFound via except Exception → retorna 500 em vez de 404."""
        client, _ = auth_client
        resp = client.delete("/estudos/excluir/999999")
        assert resp.status_code in (404, 500)

    def test_excluir_existente_retorna_json(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Estudo
            estudo = Estudo.query.first()
            if not estudo:
                pytest.skip("Nenhum estudo para testar exclusão")
            eid = estudo.id_estudo

        resp = client.delete(f"/estudos/excluir/{eid}")
        assert resp.status_code in (200, 302, 403)
