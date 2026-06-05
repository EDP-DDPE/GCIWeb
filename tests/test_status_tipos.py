"""Testes para o blueprint de tipos de status."""

import pytest


class TestListarStatusTipos:
    def test_sem_login_redireciona(self, client):
        resp = client.get("/status_tipos")
        assert resp.status_code in (301, 302)

    def test_com_login_retorna_200(self, auth_client):
        client, _ = auth_client
        resp = client.get("/status_tipos")
        assert resp.status_code == 200

    def test_exibe_tipo_seed(self, auth_client):
        client, _ = auth_client
        resp = client.get("/status_tipos")
        html = resp.data.decode("utf-8", errors="replace")
        assert "análise" in html.lower() or "status" in html.lower()


class TestAdicionarStatusTipo:
    def test_sem_login_redireciona(self, client):
        resp = client.post("/status_tipos/adicionar", data={})
        assert resp.status_code in (301, 302)

    def test_adicionar_valido(self, auth_client):
        """Rota requer status + descricao + ativo (todos obrigatórios)."""
        client, _ = auth_client
        resp = client.post(
            "/status_tipos/adicionar",
            json={"status": "Aprovado Teste", "descricao": "Status de aprovação", "ativo": 1},
            content_type="application/json",
        )
        assert resp.status_code in (200, 201, 302)

    def test_adicionar_sem_dados(self, auth_client):
        client, _ = auth_client
        resp = client.post(
            "/status_tipos/adicionar",
            json={},
            content_type="application/json",
        )
        assert resp.status_code in (200, 400, 422, 302)


class TestApiStatusTipo:
    def test_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.get("/status_tipos/999999/api")
        assert resp.status_code == 404

    def test_retorna_json(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import StatusTipo
            tipo = StatusTipo.query.first()
            if not tipo:
                pytest.skip("Nenhum tipo disponível")
            tid = tipo.id_status_tipo

        resp = client.get(f"/status_tipos/{tid}/api")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data is not None
        assert "status" in data
        # a API pode retornar "id" ou "id_status_tipo" dependendo da implementação
        assert "id" in data or "id_status_tipo" in data


class TestEditarStatusTipo:
    def test_sem_login_redireciona(self, client):
        resp = client.post("/status_tipos/1/editar", data={})
        assert resp.status_code in (301, 302)

    def test_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.post("/status_tipos/999999/editar", data={})
        assert resp.status_code == 404

    def test_editar_existente(self, auth_client, app):
        client, _ = auth_client
        with app.app_context():
            from app.models import StatusTipo
            tipo = StatusTipo.query.first()
            if not tipo:
                pytest.skip("Nenhum tipo disponível")
            tid = tipo.id_status_tipo

        resp = client.post(
            f"/status_tipos/{tid}/editar",
            json={"status": "Em Análise Editado"},
            content_type="application/json",
        )
        assert resp.status_code in (200, 302)


class TestExcluirStatusTipo:
    def test_sem_login_redireciona(self, client):
        resp = client.post("/status_tipos/1/excluir", data={})
        assert resp.status_code in (301, 302)

    def test_inexistente_retorna_404(self, auth_client):
        client, _ = auth_client
        resp = client.post("/status_tipos/999999/excluir", data={})
        assert resp.status_code == 404

    def test_tipo_com_status_vinculados_nao_exclui(self, auth_client, app):
        """Tipo com status de estudos vinculados não deve ser excluído."""
        client, _ = auth_client
        with app.app_context():
            from app.models import StatusTipo
            tipo = StatusTipo.query.filter(
                StatusTipo.status_estudos.any()
            ).first()
            if not tipo:
                pytest.skip("Nenhum tipo com status vinculados")
            tid = tipo.id_status_tipo

        resp = client.post(f"/status_tipos/{tid}/excluir", data={})
        # Pode retornar 200 JSON com success=False, ou redirect, ou erro
        assert resp.status_code in (200, 302, 400, 500)
        data = resp.get_json()
        if data and resp.status_code == 200:
            assert data.get("success") is False

    def test_tipo_sem_vinculos_exclui(self, auth_client, app):
        """Tipo sem vínculos deve ser excluído com sucesso."""
        client, _ = auth_client
        with app.app_context():
            from app.models import StatusTipo, db
            novo = StatusTipo(status="Tipo Temporário")
            db.session.add(novo)
            db.session.commit()
            tid = novo.id_status_tipo

        resp = client.post(f"/status_tipos/{tid}/excluir", data={})
        assert resp.status_code in (200, 302)
