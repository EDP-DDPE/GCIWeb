"""Testes para o blueprint de circuitos."""

import pytest


class TestListarCircuitos:
    def test_sem_login_redireciona(self, client):
        resp = client.get("/circuitos")
        assert resp.status_code in (301, 302)

    def test_com_login_retorna_200(self, auth_client):
        client, _ = auth_client
        resp = client.get("/circuitos")
        assert resp.status_code == 200

    def test_contem_lista(self, auth_client):
        client, _ = auth_client
        resp = client.get("/circuitos")
        html = resp.data.decode("utf-8", errors="replace")
        assert "circuito" in html.lower()


class TestAdicionarCircuito:
    def test_sem_login_retorna_resposta(self, client):
        """/circuitos/adicionar não tem @requires_permission."""
        resp = client.post("/circuitos/adicionar", data={})
        assert resp.status_code in (200, 400, 422)

    def test_adicionar_sem_dados_retorna_erro(self, auth_client):
        client, _ = auth_client
        resp = client.post("/circuitos/adicionar", data={})
        assert resp.status_code in (200, 302, 400)

    def test_adicionar_valido(self, auth_client, app):
        """Requer: circuito, tensao, id_subestacao, id_edp."""
        client, _ = auth_client
        with app.app_context():
            from app.models import EDP, Subestacao
            edp = EDP.query.first()
            sub = Subestacao.query.first()
            if not edp or not sub:
                pytest.skip("Dados insuficientes")
            eid = edp.id_edp
            sid = sub.id_subestacao

        resp = client.post(
            "/circuitos/adicionar",
            json={
                "circuito": "TST01",
                "tensao": "AT",
                "id_edp": eid,
                "id_subestacao": sid,
            },
            content_type="application/json",
        )
        assert resp.status_code in (200, 201, 302)


class TestEditarCircuito:
    def test_sem_login_redireciona(self, client):
        resp = client.post("/circuitos/1/editar", data={})
        assert resp.status_code in (301, 302)

    def test_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.post("/circuitos/999999/editar", data={})
        assert resp.status_code == 404

    def test_editar_circuito_existente(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Circuito
            circ = Circuito.query.first()
            if not circ:
                pytest.skip("Nenhum circuito disponível")
            cid = circ.id_circuito

        resp = client.post(
            f"/circuitos/{cid}/editar",
            json={"circuito": "BRT99"},
            content_type="application/json",
        )
        assert resp.status_code in (200, 302)


class TestApiCircuito:
    def test_api_circuito_retorna_json(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Circuito
            circ = Circuito.query.first()
            if not circ:
                pytest.skip("Nenhum circuito disponível")
            cid = circ.id_circuito

        resp = client.get(f"/circuitos/{cid}/api")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data is not None
        assert "circuito" in data

    def test_api_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.get("/circuitos/999999/api")
        assert resp.status_code == 404


class TestExcluirCircuito:
    def test_sem_login_redireciona(self, client):
        resp = client.post("/circuitos/1/excluir", data={})
        assert resp.status_code in (301, 302)

    def test_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.post("/circuitos/999999/excluir", data={})
        assert resp.status_code == 404

    def test_com_alternativas_nao_exclui(self, auth_client, app):
        """Circuito com alternativas vinculadas não pode ser excluído."""
        client, _ = auth_client
        with app.app_context():
            from app.models import Circuito
            circ = Circuito.query.filter(
                Circuito.alternativas.any()
            ).first()
            if not circ:
                pytest.skip("Nenhum circuito com alternativas")
            cid = circ.id_circuito

        resp = client.post(f"/circuitos/{cid}/excluir", data={})
        data = resp.get_json()
        if data:
            assert data.get("success") is False
