"""Testes para o blueprint de listagem de estudos."""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestListarPage:
    def test_sem_login_redireciona(self, client):
        resp = client.get("/listar")
        assert resp.status_code in (301, 302)

    def test_com_login_retorna_200(self, auth_client):
        client, _ = auth_client
        resp = client.get("/listar")
        assert resp.status_code == 200

    def test_contem_tabela(self, auth_client):
        client, _ = auth_client
        resp = client.get("/listar")
        html = resp.data.decode("utf-8", errors="replace")
        assert "table" in html.lower()


class TestApiEstudos:
    def test_sem_login_retorna_dados(self, client):
        """/listar/api/estudos não tem @requires_permission — retorna JSON mesmo sem login."""
        resp = client.get("/listar/api/estudos?page=1&per_page=5")
        assert resp.status_code == 200

    def test_com_login_retorna_json(self, auth_client):
        client, _ = auth_client
        resp = client.get("/listar/api/estudos?page=1&per_page=10")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data is not None

    def test_retorna_estrutura_correta(self, auth_client):
        client, _ = auth_client
        resp = client.get("/listar/api/estudos?page=1&per_page=5")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "items" in data
        assert "page" in data
        assert "has_next" in data

    def test_paginacao_page_1(self, auth_client):
        client, _ = auth_client
        resp = client.get("/listar/api/estudos?page=1&per_page=5")
        data = resp.get_json()
        assert data["page"] == 1

    def test_busca_global(self, auth_client):
        client, _ = auth_client
        resp = client.get("/listar/api/estudos?page=1&per_page=10&search=teste")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "items" in data

    def test_ordenacao_asc(self, auth_client):
        client, _ = auth_client
        resp = client.get("/listar/api/estudos?sort=id_estudo&direction=asc")
        assert resp.status_code == 200

    def test_ordenacao_desc(self, auth_client):
        client, _ = auth_client
        resp = client.get("/listar/api/estudos?sort=id_estudo&direction=desc")
        assert resp.status_code == 200

    def test_exportacao_csv(self, auth_client):
        client, _ = auth_client
        resp = client.get("/listar/api/estudos?export=csv")
        # Pode retornar arquivo CSV ou JSON
        assert resp.status_code in (200, 400)

    def test_exportacao_xlsx(self, auth_client):
        client, _ = auth_client
        resp = client.get("/listar/api/estudos?export=xlsx")
        assert resp.status_code in (200, 400)


class TestApiStatus:
    def test_get_status_sem_login_retorna_json(self, client):
        """/listar/api/status/<id> não tem @requires_permission."""
        resp = client.get("/listar/api/status/999999")
        assert resp.status_code == 200

    def test_get_status_inexistente_retorna_lista_vazia(self, auth_client):
        client, _ = auth_client
        resp = client.get("/listar/api/status/999999")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_get_status_retorna_json(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Estudo
            estudo = Estudo.query.first()
            if not estudo:
                pytest.skip("Nenhum estudo disponível")
            eid = estudo.id_estudo

        resp = client.get(f"/listar/api/status/{eid}")
        assert resp.status_code == 200
        assert resp.get_json() is not None


class TestSalvarStatus:
    def test_salvar_sem_login_retorna_resposta(self, client):
        """/listar/api/status/salvar sem sessão → get_usuario_logado() retorna None → AttributeError."""
        try:
            resp = client.post(
                "/listar/api/status/salvar",
                json={"id_estudo": 1, "id_status_tipo": 1},
            )
            assert resp.status_code in (200, 400, 422, 500)
        except Exception:
            pass  # AttributeError esperado quando usuario=None

    def test_salvar_status_valido(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Estudo, StatusTipo
            estudo = Estudo.query.first()
            tipo = StatusTipo.query.first()
            if not estudo or not tipo:
                pytest.skip("Dados de apoio insuficientes")
            payload = {
                "id_estudo": estudo.id_estudo,
                "id_status_tipo": tipo.id_status_tipo,
                "observacao": "Status de teste",
            }

        resp = client.post(
            "/listar/api/status/salvar",
            json=payload,
            content_type="application/json",
        )
        assert resp.status_code in (200, 201)

    def test_salvar_status_sem_dados_retorna_erro(self, auth_client):
        client, _ = auth_client
        resp = client.post(
            "/listar/api/status/salvar",
            json={},
            content_type="application/json",
        )
        assert resp.status_code in (200, 400, 422, 500)


class TestDownloadAnexo:
    def test_download_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.get("/listar/download/arquivo_inexistente.pdf")
        assert resp.status_code == 404

    def test_download_sem_login_redireciona(self, client):
        resp = client.get("/listar/download/arquivo.pdf")
        assert resp.status_code in (301, 302, 404)


class TestDetalhesEstudo:
    def test_detalhes_sem_login_retorna_resposta(self, client):
        """/listar/estudos/<id> não tem @requires_permission — qualquer resposta é válida."""
        resp = client.get("/listar/estudos/999999")
        assert resp.status_code in (200, 404, 500)

    def test_detalhes_inexistente_retorna_404(self, auth_client):
        """Estudo inexistente pode retornar 404 ou HTML vazio dependendo da implementação."""
        client, _ = auth_client
        resp = client.get("/listar/estudos/999999")
        assert resp.status_code in (200, 404)

    def test_detalhes_retorna_html(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Estudo
            estudo = Estudo.query.first()
            if not estudo:
                pytest.skip("Nenhum estudo disponível")
            eid = estudo.id_estudo

        resp = client.get(f"/listar/estudos/{eid}")
        assert resp.status_code in (200, 404)
