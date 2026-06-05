"""Testes para o blueprint de empresas."""

import pytest


class TestListarEmpresas:
    def test_sem_login_redireciona(self, client):
        resp = client.get("/empresas")
        assert resp.status_code in (301, 302)

    def test_com_login_retorna_200(self, auth_client):
        client, _ = auth_client
        resp = client.get("/empresas")
        assert resp.status_code == 200

    def test_lista_contem_empresa_seed(self, auth_client, app):
        client, _ = auth_client
        resp = client.get("/empresas")
        html = resp.data.decode("utf-8", errors="replace")
        assert resp.status_code == 200
        # Verifica que algum dado de empresa aparece
        assert "empresa" in html.lower()


class TestApiEmpresa:
    def test_sem_login_retorna_404_ou_200(self, client):
        """/empresas/<id>/api — verificar se requer auth."""
        resp = client.get("/empresas/999999/api")
        assert resp.status_code in (200, 301, 302, 404)

    def test_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.get("/empresas/999999/api")
        assert resp.status_code == 404

    def test_retorna_json_completo(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Empresa
            emp = Empresa.query.first()
            if not emp:
                pytest.skip("Nenhuma empresa disponível")
            eid = emp.id_empresa

        resp = client.get(f"/empresas/{eid}/api")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data is not None
        assert "cnpj" in data
        assert "id" in data or "id_empresa" in data
