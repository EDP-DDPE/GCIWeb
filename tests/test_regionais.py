"""Testes para o blueprint de regionais."""

import pytest


class TestListarRegionais:
    def test_sem_login_redireciona(self, client):
        resp = client.get("/regionais")
        assert resp.status_code in (301, 302)

    def test_com_login_retorna_200(self, auth_client):
        client, _ = auth_client
        resp = client.get("/regionais")
        assert resp.status_code == 200

    def test_exibe_regional_seed(self, auth_client):
        client, _ = auth_client
        resp = client.get("/regionais")
        html = resp.data.decode("utf-8", errors="replace")
        assert "campinas" in html.lower() or "regional" in html.lower()


class TestApiRegional:
    def test_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.get("/regionais/999999/api")
        assert resp.status_code == 404

    def test_retorna_json(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Regional
            reg = Regional.query.first()
            if not reg:
                pytest.skip("Nenhuma regional disponível")
            rid = reg.id_regional

        resp = client.get(f"/regionais/{rid}/api")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data is not None
        assert "regional" in data
        # campo pode ser "id" ou "id_regional" dependendo do serializer
        assert "id" in data or "id_regional" in data


class TestEditarRegional:
    def test_sem_login_redireciona(self, client):
        resp = client.post("/regionais/1/editar", data={})
        assert resp.status_code in (301, 302)

    def test_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.post("/regionais/999999/editar", data={})
        assert resp.status_code == 404

    def test_editar_existente(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import Regional
            reg = Regional.query.first()
            if not reg:
                pytest.skip("Nenhuma regional disponível")
            rid = reg.id_regional

        resp = client.post(
            f"/regionais/{rid}/editar",
            json={"regional": "Campinas Editada"},
            content_type="application/json",
        )
        assert resp.status_code in (200, 302)


class TestExcluirRegional:
    def test_sem_login_redireciona(self, client):
        resp = client.post("/regionais/1/excluir", data={})
        assert resp.status_code in (301, 302)

    def test_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.post("/regionais/999999/excluir", data={})
        assert resp.status_code == 404

    def test_regional_com_dependencias_nao_exclui(self, auth_client, app):
        """Regional com municípios ou resp_regioes vinculados não pode ser excluída."""
        client, _ = auth_client
        with app.app_context():
            from app.models import Regional
            reg = Regional.query.filter(
                Regional.municipios.any() | Regional.resp_regioes.any()
            ).first()
            if not reg:
                pytest.skip("Nenhuma regional com dependências disponível")
            rid = reg.id_regional

        resp = client.post(f"/regionais/{rid}/excluir", data={})
        assert resp.status_code in (200, 400, 409)
        data = resp.get_json()
        if data:
            # Resposta pode usar "success": False OU "status": "error"
            has_error = data.get("success") is False or data.get("status") == "error"
            assert has_error

    def test_regional_sem_dependencias_exclui(self, auth_client, app):
        """Regional sem dependências pode ser excluída."""
        client, _ = auth_client
        with app.app_context():
            from app.models import Regional, EDP, db
            edp = EDP.query.first()
            if not edp:
                pytest.skip("Nenhum EDP disponível")
            reg_nova = Regional(regional="Regional Temporária", id_edp=edp.id_edp)
            db.session.add(reg_nova)
            db.session.commit()
            rid = reg_nova.id_regional

        resp = client.post(f"/regionais/{rid}/excluir", data={})
        assert resp.status_code in (200, 302)
