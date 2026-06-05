"""Testes para o blueprint de municípios."""

import pytest


class TestListarMunicipios:
    def test_sem_login_redireciona(self, client):
        resp = client.get("/municipios")
        assert resp.status_code in (301, 302)

    def test_com_login_retorna_200(self, auth_client):
        client, _ = auth_client
        resp = client.get("/municipios")
        assert resp.status_code == 200

    def test_exibe_municipio_seed(self, auth_client):
        client, _ = auth_client
        resp = client.get("/municipios")
        assert resp.status_code == 200
        html = resp.data.decode("utf-8", errors="replace")
        assert "municipio" in html.lower() or "município" in html.lower()


class TestApiMunicipio:
    def test_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.get("/municipios/999999/api")
        assert resp.status_code == 404

    def test_retorna_json(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Municipio
            mun = Municipio.query.first()
            if not mun:
                pytest.skip("Nenhum município disponível")
            mid = mun.id_municipio

        resp = client.get(f"/municipios/{mid}/api")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data is not None
        assert "municipio" in data
        assert "id" in data or "id_municipio" in data


class TestEditarMunicipio:
    def test_sem_login_redireciona(self, client):
        resp = client.post("/municipios/1/editar", data={})
        assert resp.status_code in (301, 302)

    def test_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.post("/municipios/999999/editar", data={})
        assert resp.status_code == 404

    def test_editar_municipio_existente(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Municipio, Regional
            mun = Municipio.query.first()
            reg = Regional.query.first()
            if not mun or not reg:
                pytest.skip("Dados insuficientes")
            mid = mun.id_municipio
            rid = reg.id_regional

        resp = client.post(
            f"/municipios/{mid}/editar",
            json={"municipio": "Campinas Editado", "id_regional": rid},
            content_type="application/json",
        )
        assert resp.status_code in (200, 302)


class TestRegionaisPorEstado:
    def test_retorna_json(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import EDP
            edp = EDP.query.first()
            if not edp:
                pytest.skip("Nenhum EDP disponível")
            eid = edp.id_edp

        resp = client.get(f"/municipios/{eid}/regional")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
