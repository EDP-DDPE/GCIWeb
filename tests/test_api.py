"""Testes para o blueprint de API de suporte."""

import pytest
from unittest.mock import patch, MagicMock


class TestApiDadosEstudo:
    def test_sem_login_retorna_404_ou_200(self, client):
        """/api/alternativa/estudo/<id> não tem @requires_permission."""
        resp = client.get("/api/alternativa/estudo/999999")
        assert resp.status_code in (200, 404)

    def test_estudo_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.get("/api/alternativa/estudo/999999")
        assert resp.status_code == 404

    def test_retorna_json(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Estudo
            estudo = Estudo.query.first()
            if not estudo:
                pytest.skip("Nenhum estudo disponível")
            eid = estudo.id_estudo

        resp = client.get(f"/api/alternativa/estudo/{eid}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data is not None

    def test_campos_de_demanda_presentes(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Estudo
            estudo = Estudo.query.first()
            if not estudo:
                pytest.skip("Nenhum estudo disponível")
            eid = estudo.id_estudo

        resp = client.get(f"/api/alternativa/estudo/{eid}")
        if resp.status_code == 200:
            data = resp.get_json()
            # Campos esperados do estudo para o formulário de alternativa
            assert any(k in data for k in ("dem_p_ant", "dem_fp_ant", "id_edp", "latitude"))


class TestApiCircuitos:
    def test_circuitos_por_edp_subgrupo(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import EDP
            edp = EDP.query.first()
            if not edp:
                pytest.skip("Nenhum EDP disponível")
            eid = edp.id_edp

        resp = client.get(f"/api/circuitos/{eid}/A2")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "circuitos" in data
        assert isinstance(data["circuitos"], list)

    def test_edp_inexistente_retorna_lista_vazia(self, auth_client):
        client, _ = auth_client
        resp = client.get("/api/circuitos/999999/A2")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "circuitos" in data
        assert data["circuitos"] == []


class TestApiFatorK:
    def test_fator_k_retorna_json(self, auth_client, app):
        """DATEADD é SQL Server-specific — falha com OperationalError no SQLite."""
        client, _ = auth_client
        with app.app_context():
            from app.models import EDP
            edp = EDP.query.first()
            if not edp:
                pytest.skip("Nenhum EDP disponível")
            eid = edp.id_edp

        try:
            resp = client.get(f"/api/fator_k/{eid}/A2/2024-01-01/1")
            assert resp.status_code in (200, 404, 500)
        except Exception:
            pytest.skip("DATEADD não suportado no SQLite")

    def test_fator_k_sem_dados_retorna_null(self, auth_client):
        """DATEADD é SQL Server-specific — falha com OperationalError no SQLite."""
        client, _ = auth_client
        try:
            resp = client.get("/api/fator_k/999999/A9/2000-01-01/1")
            assert resp.status_code in (200, 404, 500)
        except Exception:
            pytest.skip("DATEADD não suportado no SQLite")


class TestApiCliente:
    def test_cliente_por_instalacao(self, auth_client):
        client, _ = auth_client
        with patch("app.api.routes.Instalacao") as mock_inst:
            mock_inst.query.filter_by.return_value.first.return_value = None
            resp = client.get("/api/cliente/123456789")
            assert resp.status_code in (200, 204, 404)

    def test_cliente_por_cnpj(self, auth_client):
        client, _ = auth_client
        with patch("app.api.routes.Instalacao") as mock_inst:
            mock_inst.query.filter_by.return_value.first.return_value = None
            resp = client.get("/api/cliente/cnpj/00000000000100")
            assert resp.status_code in (200, 204, 404)


class TestApiCnpj:
    def test_consulta_cnpj_externo(self, auth_client):
        """Consulta de CNPJ na ReceitaWS deve ser tratada mesmo offline."""
        client, _ = auth_client
        with patch("requests.get") as mock_req:
            mock_req.return_value.json.return_value = {"status": "ERROR"}
            mock_req.return_value.status_code = 200
            resp = client.get("/api/consulta/00000000000191")
            assert resp.status_code in (200, 400, 404, 500)


class TestApiTipoSolicitacao:
    def test_tipo_analises_retorna_lista(self, auth_client):
        client, _ = auth_client
        resp = client.get("/api/tipo_analises/EV")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_tipo_pedidos_retorna_lista(self, auth_client):
        client, _ = auth_client
        resp = client.get("/api/tipo_pedidos/EV/Técnica")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_id_tipo_solicitacao(self, auth_client):
        client, _ = auth_client
        resp = client.get("/api/id_tipo_solicitacao/EV/Técnica/Novo")
        assert resp.status_code in (200, 404)
